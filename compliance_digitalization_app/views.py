from django.shortcuts import render
from django.http import HttpResponse, HttpResponsePermanentRedirect
from compliance_digitalization_app.models import *
import xlrd 
import os
import xlwt

from django.utils.timezone import get_current_timezone
from datetime import datetime, timedelta
import logging
# logger = logging.getLogger(__file__)
import requests
from bs4 import BeautifulSoup
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
import json
#from background_task import background


# Create your views here.
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from threading import Timer
from dateutil.relativedelta import *
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
from io import StringIO, BytesIO
from xhtml2pdf import pisa
from django.db.models import Q
from django.shortcuts import redirect

def per(request):


    input_type = ContentType.objects.get_for_model(InputModule, for_concrete_model=True)
    mitigation_type = ContentType.objects.get_for_model(MitigationPlan, for_concrete_model=True)

    user = User.objects.get(id=2)
    # any permission check will cache the current set of permissions

    input_module_permissions = Permission.objects.filter(content_type=input_type)


    mitigation_plan_permissions = Permission.objects.filter(content_type=mitigation_type)

    for i, m in zip(input_module_permissions, mitigation_plan_permissions):
       

        user.user_permissions.add(i)
        user.user_permissions.add(m)
        
        print(i.id)
        print(m.id)


 
   
    # user.has_perm('compliance_digitalization_app.view_inputmodule')
    # user.save()

    # print(content_type)

@login_required(login_url='/admin')
def division_status(request):
    com_owner = ComplianceOwner.objects.all()
    com_owner_list = []
    com_owner_data_list = []

    if com_owner:
        for i in com_owner:
            responder_input_module = InputModule.objects.filter(compliance_owner_function__id=i.id, objects_status=2, current_status__in=[1, 2])
            yes = responder_input_module.filter(current_status=1).count()
            no = responder_input_module.filter(current_status=2).count()
            yes_percentage = 0
            no_percentage = 0
            if yes > 0:
                yes_value = yes * 100
                yes_percentage = (100 * yes_value) / (responder_input_module.count() * 100)

            if no > 0:
                no_value = no * 100
                no_percentage = (100 * no_value) / (responder_input_module.count() * 100)
            
            com_owner_list.append(i.name)
            com_owner_data_list.append([(yes_percentage), (no_percentage)])

    data = {
        'com_owner_list': com_owner_list,
        'com_owner_data_list': com_owner_data_list,
    }
    return JsonResponse(data)

@login_required(login_url='/admin')
def compliance_status(request):
    yes_value = 0
    no_value = 0
    total_count=0
    if request.user.user_type == '1':
        all_object = InputModule.objects.filter(current_status__in=['1', '2'], objects_status='2')
        yes_value = all_object.filter(current_status='1').count() * 100
        no_value = all_object.filter(current_status='2').count() * 100
        total_count=all_object.count()

    elif request.user.user_type == '2':

        filter_input = InputModule.objects.filter(compliance_owner_function=request.user.compliance_owner, current_status__in=['1', '2'], objects_status='2')
        
        yes_value = filter_input.filter(current_status='1').count()* 100
        no_value = filter_input.filter(current_status='2').count()* 100
        total_count=filter_input.count()


    elif request.user.user_type == '3' or request.user.user_type == '4':
        filter_input = InputModule.objects.filter(compliance_owner_function=request.user.compliance_owner, functional_SPOC=request.user, current_status__in=['1', '2'], objects_status=1)
        yes_value = filter_input.filter(current_status='1').count() * 100
        no_value = filter_input.filter(current_status='2').count() * 100
        total_count=filter_input.count()


    yes_percentage=0
    no_percentage=0
    if yes_value>0:
        yes_percentage = (100 * yes_value) / (total_count * 100)
    if no_value>0:
        no_percentage = (100 * no_value) / (total_count * 100)


    print(yes_percentage, no_percentage)


    data = {'yes_percentage': (yes_percentage), 'no_percentage':(no_percentage)}
    return JsonResponse(data)

@login_required(login_url='/admin')
def add_all_framing_itms(request):
    loc =  os.path.dirname(__file__)+"/Checklist.xlsx"
    wb = xlrd.open_workbook(loc) 
    sheet = wb.sheet_by_index(0)





    for j in range(sheet.nrows): 
        i=j+1

        framing = InputFramingModule()



        framing.title=sheet.cell_value(i, 1)
        framing.benchmark=sheet.cell_value(i, 4)
        framing.source_of_obligation=sheet.cell_value(i, 5)
        framing.clause_no='0'

        if sheet.cell_value(i, 3) == 'Major':

            framing.type= '1'
        else:
           framing.type='2'



        network = ComplianceCategory.objects.filter(name=sheet.cell_value(i, 6))

        if network:


            framing.compliance_category= network[0]
        else:
            create = ComplianceCategory.objects.create(name=sheet.cell_value(i, 6))

            framing.compliance_category=create
        


        requirement=sheet.cell_value(i, 7).upper()
        if requirement == "Yes/No Statement only".upper():
            framing.Input_Requirement="1"

        if sheet.cell_value(i, 8) == 'Yes':
            framing.proof_of_compliance= True
        else:
            framing.proof_of_compliance= False
       
        framing.save()


        input_module = InputModule()
        input_module.input_framing_module = framing
        input_module.compliance_statement = framing.title

        if sheet.cell_value(i, 2) == 'Yes':

            input_module.current_status = '1'
        else:
           input_module.current_status = '2' 

           input_module.root_cause =  sheet.cell_value(i, 20)
           input_module.mitigation_plan_validated_by =  sheet.cell_value(i, 23)
           input_module.mitigation_plan_Statement =  sheet.cell_value(i, 21)
        
        input_module.create_date = datetime.today().date()
        input_module.objects_status= '2'



        co_owner = ComplianceOwner.objects.filter(name=sheet.cell_value(i, 10))

        if co_owner:


            input_module.compliance_owner_function = co_owner[0]
        else:
            create = ComplianceOwner.objects.create(name=sheet.cell_value(i, 10))
            input_module.compliance_owner_function = create

        fun_spoc = User.objects.filter(username=sheet.cell_value(i, 12))

        if fun_spoc:


            input_module.functional_SPOC = fun_spoc[0]
        else:
            user = User.objects.create(username=sheet.cell_value(i, 12), password='123456')


            input_module.functional_SPOC = user

        input_module.save()


        input_framing_inline = InputFramingModuleInlineInformation()

        co_owner = ComplianceOwner.objects.filter(name=sheet.cell_value(i, 10))

        if co_owner:


            input_framing_inline.compliance_owner_function = co_owner[0]


        fun_spoc = User.objects.filter(username=sheet.cell_value(i, 12))

        if fun_spoc:


            input_framing_inline.functional_SPOC = fun_spoc[0]
        else:
            
            pass

        input_framing_inline.email_of_SPOC = sheet.cell_value(i, 12)
        input_framing_inline.LM_of_SPOC = sheet.cell_value(i, 13)

        input_framing_inline.email_of_SPOC_LM = sheet.cell_value(i, 14)
        input_framing_inline.assessment_date = datetime.today().date()
        if sheet.cell_value(i, 16):

            input_framing_inline.prior_notification = sheet.cell_value(i, 16)
        else:
           input_framing_inline.prior_notification = '1' 

        if sheet.cell_value(i, 17):

            input_framing_inline.prior_notification = sheet.cell_value(i, 17)
        else:
           input_framing_inline.prior_notification = '1' 


        frequency= sheet.cell_value(i, 9)
        
            
        if frequency=="Daily":
            input_framing_inline.assessment_frequency="1"
        if frequency=="Weekly":
            input_framing_inline.assessment_frequency="2"
        if frequency=="Fortnightly":
            input_framing_inline.assessment_frequency="3"
        if frequency=="Monthly":
            input_framing_inline.assessment_frequency="4"
        if frequency=="Bi-monthly":
            input_framing_inline.assessment_frequency="5"
        if frequency=="Quarterly":
            input_framing_inline.assessment_frequency="6"
        if frequency=="Half-yearly":
            input_framing_inline.assessment_frequency="7"
        if frequency=="Yearly":
            input_framing_inline.assessment_frequency="8"
        if frequency=="As and when required":
            input_framing_inline.assessment_frequency="9"
        if frequency=="Daily checking":
            input_framing_inline.assessment_frequency="10"
        if frequency=="Weekly checking":
            input_framing_inline.assessment_frequency="11"
        if frequency=="Quarterly checking":
            input_framing_inline.assessment_frequency="12"                
        if frequency=="Yearly checking":
            input_framing_inline.assessment_frequency="13"    

        if sheet.cell_value(i, 18):

            input_framing_inline.escalation_notification = sheet.cell_value(i, 18)
        else:
           input_framing_inline.escalation_notification = '1'

        input_framing_inline.InputFramingModule_id = framing

        input_framing_inline.input_module_id = input_module.id ### require
        input_framing_inline.save()

    return HttpResponse("<h1>ALLAH is one</h1>")

@login_required(login_url='/admin')
def export_users_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="users.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Users')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True


    columns = ['Compliance Statement', 'Source of Obligation', ' Compliance Type', 'Compliance Category',
               'Input Requirement' , 'Benchmark Value', 'Proof of compliance','Question/Note to SPOC',
               'Compliance owner function', 'Functional SPOC','Email of SPOC','LM of SPOC','Email of SPOC LM',
               'Assessment date','Assessment frequency','Prior notification','Reminder notification',
               'LM Escalation notification']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)


    font_style = xlwt.XFStyle()
    datas= InputFramingModule.objects.all()


    for row in datas:
        row_num+=1
        ws.write(row_num, 0, row.title, font_style)
        ws.write(row_num, 1, row.source_of_obligation, font_style)
        ws.write(row_num, 2, row.type, font_style)
        ws.write(row_num, 3, str(row.compliance_category), font_style)
        ws.write(row_num, 4, row.Input_Requirement, font_style)
        ws.write(row_num, 5, row.benchmark, font_style)
        ws.write(row_num, 6, "", font_style) #Proof of compliance
        ws.write(row_num, 7, str(row.question_note_to_SPOC), font_style)
        ws.write(row_num, 8, "", font_style) #Compliance owner function
        ws.write(row_num, 9, "", font_style) #Functional SPOC
        ws.write(row_num, 10, "", font_style) #Email of SPOC
        ws.write(row_num, 11, row.type, font_style) #LM of SPOC
        ws.write(row_num, 12, row.type, font_style) #Email of SPOC LM
        ws.write(row_num, 13, row.type, font_style) #Assessment date
        ws.write(row_num, 14, row.type, font_style) #Assessment frequency
        ws.write(row_num, 15, row.type, font_style) #Prior notification
        ws.write(row_num, 16, row.type, font_style) #Reminder notification
        ws.write(row_num, 17, row.type, font_style) #LM Escalation notification


    wb.save(response)
    return response

@login_required(login_url='/admin')
def input_users_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="users.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Users')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Id', 'Compliance Statement', 'Benchmark', 'source_of_obligation','Clause no',
               'Yes not input by assesse','Number/% Value/ Date input by assesse','Type', 'compliance Category',
               'Input Requirement','Question Note to SPOC','COMPLIANCE OWNER FUNCTION',
               'FUNCTIONAL SPOC','EMAIL OF SPOC','LM OF SPOC','EMAIL OF SPOC LM ','ASSESSMENT DATE ','ASSESSMENT FREQUENCY',
               'PRIOR NOTIFICATION','REMINDER NOTIFICATION','ESCALATION NOTIFICATION']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()
    datas= InputFramingModuleInlineInformation.objects

    user=request.user
    if user.user_type == '1':
        datas =datas.all()
    elif user.user_type =='2':
        user_division=user.compliance_owner
        datas=datas.filter(compliance_owner_function=user_division)
    elif user.user_type =='3' or user.user_type =='4':
        datas = datas.filter(functional_SPOC=user)


    for row in datas:

        if row.input_module_id:

            input_obj = InputModule.objects.get(id=int(row.input_module_id))

            row_num += 1
            ws.write(row_num, 0, row.InputFramingModule_id.id, font_style)
            ws.write(row_num, 1, row.InputFramingModule_id.title, font_style)
            ws.write(row_num, 2, row.InputFramingModule_id.benchmark, font_style)
            ws.write(row_num, 3, row.InputFramingModule_id.source_of_obligation, font_style)
            ws.write(row_num, 4, row.InputFramingModule_id.clause_no, font_style)
            ws.write(row_num, 5, input_obj.get_current_status_display(), font_style)
            value_no_per_date = ''

            if row.InputFramingModule_id.Input_Requirement == '3':
                value_no_per_date = input_obj.number
            elif row.InputFramingModule_id.Input_Requirement == '4':
                value_no_per_date = input_obj.date
            elif row.InputFramingModule_id.Input_Requirement == '2':
                value_no_per_date = input_obj.percentage_rate


            ws.write(row_num, 6, value_no_per_date, font_style)
            ws.write(row_num, 7, row.InputFramingModule_id.get_type_display(), font_style)
            category='' if row.InputFramingModule_id.compliance_category is None else row.InputFramingModule_id.compliance_category.name
            
            ws.write(row_num, 8, category , font_style)
            ws.write(row_num, 9, row.InputFramingModule_id.get_Input_Requirement_display(), font_style)
            ws.write(row_num, 10, row.InputFramingModule_id.question_note_to_SPOC, font_style)
            ws.write(row_num, 11, row.compliance_owner_function.name, font_style)
            ws.write(row_num, 12 , row.functional_SPOC.username, font_style)
            ws.write(row_num, 13, row.email_of_SPOC, font_style)
            ws.write(row_num, 14, row.LM_of_SPOC, font_style)
            ws.write(row_num, 15, row.email_of_SPOC_LM, font_style)
            ws.write(row_num, 16, row.assessment_date, font_style)
            ws.write(row_num, 17, row.get_assessment_frequency_display(), font_style)
            ws.write(row_num, 18, row.get_prior_notification_display(), font_style)
            ws.write(row_num, 19, row.get_reminder_notification_display(), font_style)
            ws.write(row_num, 20  , row.get_escalation_notification_display(), font_style)


    wb.save(response)
    return response

    # for row in rows:
    #     row_num += 1
    #     for col_num in range(len(row)):
    #         ws.write(row_num, col_num, row[col_num], font_style)



@login_required(login_url='/admin')
def quarter_on_quarter(request):
    if request.user.user_type == '1':
        get_input_obj_all = InputModule.objects.all()
        # get_input_obj = get_input_obj_all.filter(create_date__year=datetime.now().year, create_date__month=datetime.now().month, objects_status=2)
        logger.error("")
    return HttpResponse('pppp')

@login_required(login_url='/admin')
def notice_board(request):
    if request.GET.get('page'):
        URL = 'http://www.btrc.gov.bd/notice-board?page='+ request.GET.get('page')
    else:
        URL = 'http://www.btrc.gov.bd/notice-board'
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    find_class_div = soup.find_all(class_='item-list')
    all_anchor= soup.select(".views-row a")


    for a in all_anchor:
        a['href']="http://www.btrc.gov.bd"+a['href']

    print(type(find_class_div[:2]))
    data={'news':find_class_div[:2]} 
    return render(request, 'Compliance/notices.html',data)




@login_required(login_url='/admin')
def file_delete(request):
    if request.POST and request.user.is_authenticated:


        get_input = InputFramingModule.objects.get(id=request.POST.get('id'))
        if get_input:


            filter_input = InputModule.objects.filter(input_framing_module=get_input.id).last()

            filter_input.proof_of_compliance.delete(save=True)

            get_input.attachment.delete(save=True)


        return JsonResponse({'data': 'true'})


@login_required(login_url='/admin')
def responded_history_per_compliance(request, id):
    get_inputs = ''
    get_inputs = InputModule.objects.filter(input_framing_module=id, objects_status=2)

    number_of_item = 10

    paginator = Paginator(get_inputs, number_of_item)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'admin/responded_history.html',{ 'page_obj':page_obj})


@login_required(login_url='/admin')
def user_sort(request):

    

    if request.POST:

        all_users = User.objects.all()

        result = list(set(list(all_users.values_list('id', flat=True))) - set(list(all_users.filter(compliance_owner=request.POST.get('id')).values_list('id', flat=True))))
    
        response_data = {}


        response_data['list'] = result


        return JsonResponse(response_data)


class ReCallClass(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


@login_required(login_url='/admin')
def Reminder_method(name):
   

    current_date = datetime.today()

    get_objs = InputFramingModuleInlineInformation.objects.all()

    
    for i in get_objs:

        filter_input_module = InputModule.objects.filter(input_framing_module=i.InputFramingModule_id).last()


        if i.assessment_frequency == '1':

            if current_date.date() > filter_input_module.create_date:

                filter_input_module.pk = None
                filter_input_module.objects_status = 1
                filter_input_module.create_date = datetime.now()
                filter_input_module.receive_date = None
                filter_input_module.user_comment = ''
                filter_input_module.manager_comment = ''
                filter_input_module.number = None
                filter_input_module.date = None
                filter_input_module.percentage_rate = None
                filter_input_module.current_status = ''
                filter_input_module.compliance_question = ''
                filter_input_module.mitigation_plan_validated_by = ''
                filter_input_module.root_cause = ''
                filter_input_module.mitigation_plan_Statement = ''

                filter_input_module.save()
        
        elif i.assessment_frequency == '2':
            
            if (filter_input_module.create_date+ relativedelta(days=7)) < current_date.date():

                filter_input_module.pk = None
                filter_input_module.objects_status = 1
                filter_input_module.create_date = datetime.now()
                filter_input_module.receive_date = None
                filter_input_module.user_comment = ''
                filter_input_module.manager_comment = ''
                filter_input_module.number = None
                filter_input_module.date = None
                filter_input_module.percentage_rate = None
                filter_input_module.current_status = ''
                filter_input_module.compliance_question = ''
                filter_input_module.mitigation_plan_validated_by = ''
                filter_input_module.root_cause = ''
                filter_input_module.mitigation_plan_Statement = ''

                filter_input_module.save()

        elif i.assessment_frequency == '3':

            if (filter_input_module.create_date+ relativedelta(days=15)) < current_date.date():


                filter_input_module.pk = None
                filter_input_module.objects_status = 1
                filter_input_module.create_date = datetime.now()
                filter_input_module.receive_date = None
                filter_input_module.user_comment = ''
                filter_input_module.manager_comment = ''
                filter_input_module.number = None
                filter_input_module.date = None
                filter_input_module.percentage_rate = None
                filter_input_module.current_status = ''
                filter_input_module.compliance_question = ''
                filter_input_module.mitigation_plan_validated_by = ''
                filter_input_module.root_cause = ''
                filter_input_module.mitigation_plan_Statement = ''

                filter_input_module.save()
                

        elif i.assessment_frequency == '4':

            if (filter_input_module.create_date+ relativedelta(months=1)) < current_date.date():

                filter_input_module.pk = None
                filter_input_module.objects_status = 1
                filter_input_module.create_date = datetime.now()
                filter_input_module.receive_date = None
                filter_input_module.user_comment = ''
                filter_input_module.manager_comment = ''
                filter_input_module.number = None
                filter_input_module.date = None
                filter_input_module.percentage_rate = None
                filter_input_module.current_status = ''
                filter_input_module.compliance_question = ''
                filter_input_module.mitigation_plan_validated_by = ''
                filter_input_module.root_cause = ''
                filter_input_module.mitigation_plan_Statement = ''

                filter_input_module.save()

        elif i.assessment_frequency == '6':
            

            if (filter_input_module.create_date+ relativedelta(months=4)) < current_date.date():

 
                filter_input_module.pk = None
                filter_input_module.objects_status = 1
                filter_input_module.create_date = datetime.now()
                filter_input_module.receive_date = None
                filter_input_module.user_comment = ''
                filter_input_module.manager_comment = ''
                filter_input_module.number = None
                filter_input_module.date = None
                filter_input_module.percentage_rate = None
                filter_input_module.current_status = ''
                filter_input_module.compliance_question = ''
                filter_input_module.mitigation_plan_validated_by = ''
                filter_input_module.root_cause = ''
                filter_input_module.mitigation_plan_Statement = ''

                filter_input_module.save()
                            

        elif i.assessment_frequency == '7':

            if (filter_input_module.create_date+ relativedelta(months=6)) < current_date.date():


                filter_input_module.pk = None
                filter_input_module.objects_status = 1
                filter_input_module.create_date = datetime.now()
                filter_input_module.receive_date = None
                filter_input_module.user_comment = ''
                filter_input_module.manager_comment = ''
                filter_input_module.number = None
                filter_input_module.date = None
                filter_input_module.percentage_rate = None
                filter_input_module.current_status = ''
                filter_input_module.compliance_question = ''
                filter_input_module.mitigation_plan_validated_by = ''
                filter_input_module.root_cause = ''
                filter_input_module.mitigation_plan_Statement = ''

                filter_input_module.save()

    



        elif i.assessment_frequency == '8':

            if (filter_input_module.create_date+ relativedelta(years=1)) < current_date.date():
                filter_input_module.pk = None
                filter_input_module.objects_status = 1
                filter_input_module.create_date = datetime.now()
                filter_input_module.receive_date = None
                filter_input_module.user_comment = ''
                filter_input_module.manager_comment = ''
                filter_input_module.number = None
                filter_input_module.date = None
                filter_input_module.percentage_rate = None
                filter_input_module.current_status = ''
                filter_input_module.compliance_question = ''
                filter_input_module.mitigation_plan_validated_by = ''
                filter_input_module.root_cause = ''
                filter_input_module.mitigation_plan_Statement = ''

                filter_input_module.save()

    return HttpResponse('Yes')

# rt = ReCallClass(2, Reminder_method, "")


@login_required(login_url='/admin')
def QoQ_excution(request):
    comp_percen=0
    non_percen=0
    current_date= datetime.now()

    get_current_month = 0
    get_last_date = 0
    if current_date.month < 4:
        get_current_month = 3
        get_last_date = 31

    elif current_date.month > 3 and current_date.month < 7:
        get_current_month = 6
        get_last_date = 30


    elif current_date.month > 6 and current_date.month < 10:
        get_current_month= 9
        get_last_date = 30

    else:
       get_current_month = 12 
       get_last_date = 31


    # current_month_data= InputModule.objects.filter(create_date__month__lte=get_current_month,create_date__month__gte= (get_current_month-2),
    #                                               create_date__year=current_date.year, objects_status='2')


    current_month_data= InputModule.objects.filter(create_date__month=current_date.month,
                                                  create_date__year=current_date.year, objects_status='2')
    
    complianc_count= current_month_data.filter(current_status='1').count()
    non_complianc_count= current_month_data.filter(current_status='2').count()
    total_count=current_month_data.count()
    if total_count>0:
        comp_percen=(complianc_count*100)/total_count
        non_percen=(non_complianc_count*100)/total_count
        exist_qoq = QuarterOnQuarter.objects.filter(YearMonth__month=current_date.month,
                                            YearMonth__year=current_date.year).all()



        if current_date.month == get_current_month and current_date.date == get_last_date:


            if not exist_qoq:
                qoq= QuarterOnQuarter(YearMonth=current_date,CompliancePercentage=comp_percen,NonCompliancePercentage=non_percen, freeze=True)
                qoq.save()
            else:
                exist_qoq=exist_qoq[0]
                exist_qoq.CompliancePercentage=comp_percen
                exist_qoq.NonCompliancePercentage=non_percen
                exist_qoq.freeze = True
                exist_qoq.save()



 
            

            last_one_qoq = QuarterOnQuarter.objects.filter(YearMonth__month=(get_current_month-2),
                                            YearMonth__year=current_date.year)

            if last_one_qoq:
                current_month_data= InputModule.objects.filter(create_date__month=(get_current_month-2),
                                                  create_date__year=current_date.year, objects_status='2')


                complianc_count= current_month_data.filter(current_status='1').count()
                non_complianc_count= current_month_data.filter(current_status='2').count()
                total_count=current_month_data.count()
                if total_count>0:
                    comp_percen=(complianc_count*100)/total_count
                    non_percen=(non_complianc_count*100)/total_count

                    last_one_qoq[0].CompliancePercentage = comp_percen
                    last_one_qoq[0].NonCompliancePercentage = non_percen
                
                last_one_qoq[0].freeze = True

                last_one_qoq.save()




            last_two_qoq = QuarterOnQuarter.objects.filter(YearMonth__month=(get_current_month-1),
                                            YearMonth__year=current_date.year)


            if last_two_qoq:
                current_month_data= InputModule.objects.filter(create_date__month=(get_current_month-1),
                                                  create_date__year=current_date.year, objects_status='2')


                complianc_count= current_month_data.filter(current_status='1').count()
                non_complianc_count= current_month_data.filter(current_status='2').count()
                total_count=current_month_data.count()
                if total_count>0:
                    comp_percen=(complianc_count*100)/total_count
                    non_percen=(non_complianc_count*100)/total_count

                    last_one_qoq[0].CompliancePercentage = comp_percen
                    last_one_qoq[0].NonCompliancePercentage = non_percen
                
                last_one_qoq[0].freeze = True

                last_one_qoq.save()

        else:

            if not exist_qoq:
                qoq= QuarterOnQuarter(YearMonth=current_date,CompliancePercentage=comp_percen,NonCompliancePercentage=non_percen)
                qoq.save()
            else:
                exist_qoq=exist_qoq[0]
                exist_qoq.CompliancePercentage=comp_percen
                exist_qoq.NonCompliancePercentage=non_percen
                exist_qoq.save()
    print(current_month_data)
    return HttpResponse('True')

@login_required(login_url='/admin')
def GetQoQData(request):

    data= []
    compliance = []
    current_date= datetime.now()
    qoqs = QuarterOnQuarter.objects.order_by('-YearMonth')[:12]

    for qoq in qoqs:

        data.append(qoq.YearMonth.strftime('%B')+'( '+qoq.YearMonth.strftime('%Y')+')')
        compliance.append("%.2f" % qoq.CompliancePercentage)
        # data.append({
        #         "month": qoq.YearMonth.strftime('%B')+'( '+qoq.YearMonth.strftime('%Y')+')',
        #         "com": qoq.CompliancePercentage,
        #         "non_com": qoq.NonCompliancePercentage,
        #     })
    QoQ_excution(request)
    return JsonResponse([data, compliance], safe=False)

@login_required(login_url='/admin')
def list_page(request):
    all_object = ''
    if request.user.user_type == '3':
        all_object = InputModule.objects.filter(compliance_owner_function=request.user.compliance_owner, functional_SPOC=request.user, objects_status='2')


    elif request.user.user_type == '4':
         all_object = InputModule.objects.filter(compliance_owner_function=request.user.compliance_owner,functional_SPOC=request.user, objects_status='2')

    return render(request, 'admin/responded_list.html', {'all_object': all_object})


@login_required(login_url='/admin')
def pdf_page(request):
    datas = InputFramingModuleInlineInformation.objects

    user=request.user
    if user.user_type == '1':
        datas =datas.all()
    elif user.user_type =='2':
        user_division=user.compliance_owner
        datas=datas.filter(compliance_owner_function=user_division)
    elif user.user_type =='3' or user.user_type =='4':
        datas = datas.filter(functional_SPOC=user)

    input_list = []
    for row in datas:
        if row.input_module_id:
            input_filter = InputModule.objects.get(id=row.input_module_id)
            input_list.append(input_filter)


    data = {'All_modules': zip(datas,input_list)}

    # return render(request, "admin/pdf_page.html", data)

    template=get_template("admin/pdf_page.html")
    data_p=template.render(data)
    response=BytesIO()

    pdfPage=pisa.pisaDocument(BytesIO(data_p.encode("UTF-8")),response)
    if not pdfPage.err:
        return HttpResponse(response.getvalue(),content_type="application/pdf")
    else:
        return HttpResponse("Error Generating PDF")

@login_required(login_url='/admin')
def new_directive_status(request, id):



    obj = NewDirectiveCirculation.objects.get(id=id)
    get_new_dir_inline = NewDirInline.objects.filter(new_dir_cir=obj)
    get_new_dir_CI = NewDirectiveCirculationInlineInformation.objects.filter(line_num=obj)

    list_of_element = []
    n = -1
    for i in get_new_dir_inline:
        n+=1
        list_of_element.append([])

        list_of_element[n].append(i.elements_to_be_complied)
        
        
        

        if i.implementation_date and i.deadline:
            list_of_element[n].append((i.deadline).strftime("%d-%m-%Y"))
            list_of_element[n].append(i.implementation_date.strftime("%d-%m-%Y"))
            if i.implementation_date <= i.deadline:
                list_of_element[n].append('Yes')
                       
            else:
                list_of_element[n].append('No')

        elif i.deadline:
            list_of_element[n].append((i.deadline).strftime("%d-%m-%Y"))
            list_of_element[n].append('Completion date not found')
            list_of_element[n].append('Status not found')


        else:
            list_of_element[n].append('Deadline not found')
            list_of_element[n].append('Completion date not found')
            list_of_element[n].append('Status not found')





        if get_new_dir_CI:
            print(get_new_dir_CI)
            for p in get_new_dir_CI:
                print([p.line_item])
                if str(i.line_item) in list(p.line_item):
                    list_of_element[n].append(p.directive_owner_function.name)

        


    print(list_of_element)

    contex = {'list_of_element':list_of_element,
            'obj': obj,'get_new_dir_inline':get_new_dir_inline
    }




    return render(request, 'admin/new_directive_status.html', contex)




@login_required(login_url='/admin')
def new_directive_status_list(request):

    

    if request.user.user_type == '1':
        page_obj = NewDirectiveCirculation.objects.all()
        number_of_page = 10


        list_of_date = []
        list_of_division = []
        list_of_date_implement = []
        list_of_user = []
        if request.GET.get('name__icontains'):
             page_obj = NewDirectiveCirculation.objects.filter(directive_name__icontains=request.GET.get('name__icontains'))

        elif request.GET.get('id'):


            try:
                page_obj =  page_obj.filter(id=int(request.GET.get('id')))
            except Exception as e:
                page_obj = page_obj.filter(id=None)
                

        paginator = Paginator(page_obj, number_of_page) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number) 

        n = -1
        for i in page_obj:
             
            list_of_user.append([])
            list_of_division.append([])
            list_of_date.append([])
            list_of_date_implement.append([])
            new_dir = NewDirectiveCirculationInlineInformation.objects.filter(line_num=i.id)
            new_dir_inline = NewDirInline.objects.filter(new_dir_cir=i.id)
            n+=1
            if new_dir:
                list_of_division[n].append(new_dir.values_list('directive_owner_function__name', flat=True))
                list_of_user[n].append(new_dir.values_list('functional_SPOC__username', flat=True))
            if new_dir_inline:

                deadline_date = new_dir_inline.latest('deadline')
                implementation_date = new_dir_inline.latest('implementation_date')

                try:
                    list_of_date[n].append(deadline_date.deadline if deadline_date.deadline else '')
                except Exception as e:
                    list_of_date[n].append('')
                
                try:
                    list_of_date_implement[n].append(implementation_date.implementation_date if implementation_date.implementation_date else '')
                except Exception as e:
                    list_of_date[n].append('')
               
                
                    
                

        paginator_1 = Paginator(list_of_division, number_of_page) 
        page_obj_1 = paginator_1.get_page(page_number)

        paginator_2 = Paginator(list_of_date, number_of_page) 
        page_obj_2 = paginator_2.get_page(page_number)


        paginator_3 = Paginator(list_of_date_implement, number_of_page) 
        page_obj_3 = paginator_3.get_page(page_number)

        paginator_4 = Paginator(list_of_user, number_of_page) 
        page_obj_4 = paginator_4.get_page(page_number)
        
        print(list_of_division, list_of_user)

        return render(request, 'admin/new_directive_status_list.html', { 'obj':zip(page_obj,page_obj_1, page_obj_2, page_obj_3, page_obj_4),"page_obj": page_obj, 'list_of_division':list_of_division,
            'list_of_date':list_of_date, 
            'list_of_date_implement':list_of_date_implement,
            'list_of_user': list_of_user
            })

    
        
    else:

        return HttpResponsePermanentRedirect('/admin')


def delete_new_directive(request, id):
    if id:
       obj = NewDirectiveCirculation.objects.get(id=id)
       obj.delete()
       return HttpResponsePermanentRedirect('/admin/new/directive/status/list')


    
