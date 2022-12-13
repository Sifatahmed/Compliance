from django.contrib import admin
from compliance_digitalization_app.models import *
from django_admin_listfilter_dropdown.filters import (
    DropdownFilter, ChoiceDropdownFilter, RelatedDropdownFilter
)
from datetime import datetime
from django.shortcuts import redirect

class InputFramingModuleInline(admin.TabularInline):
    model = InputFramingModuleInlineInformation
    extra = 1


    fields = (
    'compliance_owner_function', 'functional_SPOC', 'email_of_SPOC',
    'LM_of_SPOC',
    'email_of_SPOC_LM', 'assessment_date', 'assessment_frequency', 'prior_notification', 'reminder_notification', 'escalation_notification'
    
    )

class NewDirectiveCirculationInline(admin.TabularInline):
    model = NewDirectiveCirculationInlineInformation
    fields = ('line_item',
   'directive_owner_function','functional_SPOC', 'email_of_SPOC','LM_of_SPOC','email_of_SPOC_LM', 
   'assessment_date', 'prior_notification', 'reminder_notification', 'escalation_notification','line_num'
    )
    template = "admin/compliance_digitalization_app/newdirectivecirculation/edit_inline/tabular.html"

class NewDirInlineAdmin(admin.TabularInline):
    model = NewDirInline
    otheruser_fields = ['upload_file', 'elements_to_be_complied', 'line_item', 'deadline', 'current_status','implementation_date','proof_of_compliance']
    
    superuser_fields = ['upload_file', 'elements_to_be_complied', 'line_item', 'deadline', 'current_status',]
    template = "admin/compliance_digitalization_app/newdirectivecirculation/edit_inline_tabular/tabular.html"

    def get_readonly_fields(self, request, obj=None):
        if request.user.user_type == '1':
            return super(NewDirInlineAdmin, self).get_readonly_fields(request, obj)

        else:
            return ('upload_file', 'elements_to_be_complied', 'line_item', 'deadline')
    


    def get_formset(self, request, obj=None, **kwargs):
        if request.user.user_type == '1' or request.user.user_type == '2':
            self.fields = self.superuser_fields
        else:
            self.fields = self.otheruser_fields
        return super(NewDirInlineAdmin, self).get_formset(request, obj, **kwargs)


 

    def get_queryset(self, request):

        qs = super(NewDirInlineAdmin, self).get_queryset(request)
        current_category = request.user.user_type
        compliance_owner = request.user.compliance_owner
        main_obj = request.resolver_match.kwargs.get('object_id')

        if current_category == '1':
            return qs

        else:
            if qs:
                get_user_permission = NewDirectiveCirculationInlineInformation.objects.filter(line_num=main_obj, directive_owner_function=compliance_owner,
                    functional_SPOC=request.user)

                # print(get_user_permission, 'get_user_permission')
                

                if get_user_permission:
                    query = []
                    for i in get_user_permission:
                        qs_sort = qs.filter(new_dir_cir=main_obj, current_status=1)
                        print(qs_sort, 'jmdhgfnh')

                        for p in i.line_item.split(','):
                            if p:       
                                filter_item = qs_sort.filter(line_item=int(p))
                                if filter_item:

                                    query.append(filter_item[0].id)
                    self.max_num = len(query)
                    print(len(query),'lllllllllllllllllllllllllllll')
                    return qs.filter(id__in=query)



    def get_max_num(self, request, obj=None, **kwargs):
        max_num = 10
        if obj and request.user.user_type > '1':
            print('pppp', obj.id)

            max_num = NewDirInline.objects.filter(new_dir_cir=obj.id).count()
            return max_num
        elif request.user.is_superuser:
            max_num = None

            return max_num



class NewDirectiveCirculationAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        if request.user.user_type == '1':
            return True
        else:
            return False
    
    readonly_fields = ()
    def change_view(self, request, object_id, form_url='', extra_context=None):

        extra_context = extra_context or {}
        extra_context['show_save_and_add_another'] = False

        if int(request.user.user_type) > 1:
            self.inlines = [NewDirInlineAdmin]

        elif int(request.user.user_type) < 2:
            self.inlines = [NewDirInlineAdmin, NewDirectiveCirculationInline]


        return super(NewDirectiveCirculationAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context,
        )

    def get_readonly_fields(self, request, obj):
        
        if obj is None:

            get_user_type= User.objects.get(id=request.user.id)
            if int(get_user_type.user_type) > 1:
                self.inlines = [NewDirInlineAdmin]

            elif int(get_user_type.user_type) < 2:
                self.inlines = [NewDirInlineAdmin, NewDirectiveCirculationInline]    
            
            return []
        else:
            if int(request.user.user_type) > 1:
                return ['directive_name']
            else:

                return []

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        current_category = request.user.user_type
        compliance_owner = request.user.compliance_owner

        if current_category == '1':
            return qs;

        elif current_category == '2':

            obj = NewDirectiveCirculationInlineInformation.objects.filter(directive_owner_function=compliance_owner).values_list('line_num', flat=True)

            return qs.filter(id__in=obj)

        else:
            
            obj = NewDirectiveCirculationInlineInformation.objects.filter(directive_owner_function=compliance_owner, functional_SPOC=request.user).values_list('line_num', flat=True)
            
            new_dir_cir_in = NewDirectiveCirculationInlineInformation.objects.filter(directive_owner_function=compliance_owner, functional_SPOC=request.user)

            obj_list = NewDirInline.objects.filter(new_dir_cir__in=obj, current_status='1').values_list('new_dir_cir', flat=True)

            obj_lists = NewDirInline.objects.filter(new_dir_cir__in=obj, current_status=1)
            
            line_item_list = []
            id_list = []
            query_list = []


            if new_dir_cir_in:
                for i in new_dir_cir_in:
                    id_list.append(i.line_num.id)

                    for n in i.line_item.split(','):
                        if n:
                            line_item_list.append(i.line_item.split(','))


                for i, g in zip(line_item_list, id_list):
                    for k in i:
                        if k is not '':
                            print(k)
                            filter_new_inline = NewDirInline.objects.filter(new_dir_cir=g,line_item=k, current_status=1)
                            if filter_new_inline:
                                query_list.append(filter_new_inline[0].new_dir_cir.id) 

                return qs.filter(id__in=query_list)
        
    def response_change(self, request, obj):

        if '_continue' in request.POST:
            return super(NewDirectiveCirculationAdmin, self).response_change(request, obj)

        elif int(request.user.user_type) == 1:
            return redirect('/admin/new/directive/status/list')

        else:
           return super(NewDirectiveCirculationAdmin, self).response_change(request, obj) 

    def response_add(self, request, obj, post_url_continue=None):
        if '_continue' in request.POST:
            return super(NewDirectiveCirculationAdmin, self).response_add(request, obj)

        elif int(request.user.user_type) == 1:
            return redirect('/admin/new/directive/status/list')

        else:
           return super(NewDirectiveCirculationAdmin, self).response_add(request, obj) 





class FileUploadInline(admin.TabularInline):
    model = MitigationPlan

class AuditUploadInline(admin.TabularInline):
    model = AuditUploads


class DocumentRepositoryUploadsUploadInline(admin.TabularInline):
    model = DocumentRepositoryUploads

class PolicyAdvocacyInline(admin.TabularInline):
    model = PolicyAdvocacyUploads

class SubjectListFilter(admin.SimpleListFilter):
    title = 'compliance_owner'
    parameter_name = 'compliance_owner'

    def lookups(self, request, model_admin):
        return (
            ('', 'compliance_owner'),
        )

    def queryset(self, request, queryset):
        if request.GET.get('compliance_owner'):
            list = InputFramingModuleInlineInformation.objects.filter(
                compliance_owner_function__id=request.GET.get(
                    'compliance_owner')).values_list('InputFramingModule_id',
                                              flat=True)
            return queryset.filter(id__in=list)


class FunctionalSPOCFilter(admin.SimpleListFilter):
    title = 'user_id'
    parameter_name = 'user_id'

    def lookups(self, request, model_admin):
        return (
            ('', 'user_id'),
        )

    def queryset(self, request, queryset):
        if request.GET.get('user_id'):
            list = InputFramingModuleInlineInformation.objects.filter(
                functional_SPOC__id=request.GET.get(
                    'user_id')).values_list('InputFramingModule_id',
                                              flat=True)
            return queryset.filter(id__in=list)


class filter_input_module_title(admin.SimpleListFilter):
    title = 'compliance_statement'
    parameter_name = 'compliance_statement'

    def lookups(self, request, model_admin):
        return (
            ('', 'compliance_statement'),
        )

    def queryset(self, request, queryset):
        if request.GET.get('compliance_statement'):

            return queryset.filter(compliance_statement__icontains=request.GET.get('compliance_statement'))


class filter_input_module_compliance_id(admin.SimpleListFilter):
    title = 'compliance_id'
    parameter_name = 'compliance_id'

    def lookups(self, request, model_admin):
        return (
            ('', 'compliance_id'),
        )

    def queryset(self, request, queryset):
        if request.GET.get('compliance_id'):
            return queryset.filter(compliance_id=request.GET.get('compliance_id'))


class InputFramingModuleAdmin(admin.ModelAdmin):
    inlines = [InputFramingModuleInline]
    fields = (
    'Get_unique_id', 'title', 'benchmark', 'source_of_obligation', 'clause_no',
    'type', 'compliance_category', 'Input_Requirement', 'proof_of_compliance', 'attachment',
    'question_note_to_SPOC')
    list_display = (
    'compliance_id', 'title', 'benchmark', 'get_compliance_performance','get_date_number_value')
    list_per_page = 200
    readonly_fields = ["unique_id",'Get_unique_id' ]
    list_filter = (
        SubjectListFilter,
        FunctionalSPOCFilter,
        
        ('title', DropdownFilter),
        ('id', DropdownFilter),
        ('compliance_category__id', DropdownFilter),
        ('source_of_obligation', DropdownFilter),
        ('type', DropdownFilter),

      
    )
    search_fields = (
    'id', 'title', 'benchmark',)
    #def compliance_id(self, obj):
    #    return obj.unique_id

    def compliance_id(self, obj):
        return str(obj.id)


    compliance_id.short_description = 'Compliance ID'


    def get_queryset(self, request):
        qs = super().get_queryset(request)
        current_category = request.user.user_type
        compliance_owner = request.user.compliance_owner

        if current_category == '1':
            return qs;

        elif current_category == '2':

            obj = InputFramingModuleInlineInformation.objects.filter(compliance_owner_function=compliance_owner).values_list('InputFramingModule_id', flat=True)

            return qs.filter(id__in=obj)

        else:

            obj = InputFramingModuleInlineInformation.objects.filter(compliance_owner_function=compliance_owner, functional_SPOC=request.user).values_list('InputFramingModule_id', flat=True)

            return qs.filter(id__in=obj)
        


    def changelist_view(self, request, extra_context=None):
        
        if request.user.user_type == '1':
                self.list_display_links = ('compliance_id', 'title',)
        else:
            self.list_display_links = (None)
        
        extra_context = {
            'compliance_owners': ComplianceOwner.objects.all(),
            'users': User.objects.all(),
            'categorys': ComplianceCategory.objects.all(),
           
        }  
        return super(InputFramingModuleAdmin, self).changelist_view(request, extra_context)

    def get_compliance_performance(self, obj):
        filter_input = InputModule.objects.filter(input_framing_module=obj, objects_status='2').last()

        if filter_input:
            return (filter_input.get_current_status_display())


    def get_date_number_value(self, obj):
        filter_input = InputModule.objects.filter(input_framing_module=obj.id).last()


        value = ''
        if filter_input:

            if filter_input.input_framing_module.Input_Requirement == '2':

                if filter_input.percentage_rate:
                    value = filter_input.percentage_rate

            elif filter_input.input_framing_module.Input_Requirement == '3':

                if filter_input.number:
                    value = filter_input.number

            elif filter_input.input_framing_module.Input_Requirement == '4':

                if filter_input.date:
                    value = filter_input.date
            return (str(value))

    get_compliance_performance.short_description = 'Status'
    get_date_number_value.short_description = 'quantifiable feedback'

class ComOblParmeter(admin.SimpleListFilter):
    title = 'compliance_obligation_page'
    parameter_name = 'compliance_obligation_page'

    def lookups(self, request, model_admin):
        return (
            ('', 'compliance_obligation_page'),
        )

    def queryset(self, request, queryset):
        return queryset




class InputModuleAdmin(admin.ModelAdmin):
    inlines = [FileUploadInline ]
    list_display = (
    'Get_unique_id', 'get_compliance_title', 'get_receive_date',
    'objects_status', 'create_date')
    readonly_fields = ["input_framing_module", "get_compliance_id",
                       "get_compliance_benchmark", "compliance_owner_function",
                       "compliance_statement", "compliance_id","compliance_question", 'Get_unique_id', 'get_benchmark']
    fields = (
    'Get_unique_id', 'compliance_statement', 'get_benchmark',
    'compliance_question',
    'current_status', 'percentage_rate', 'date', 'number', 'proof_of_compliance', 'user_comment',
    'manager_comment',
    'root_cause','mitigation_plan_Statement', 
    'target_date_of_closure', 'mitigation_plan_validated_by', 'objects_status',
    'receive_date', 'changed_file', 'functional_SPOC', 'compliance_owner_function'
    )
    search_fields = (
    'input_framing_module_unique_id', 'user_comment')


    list_filter = (
        filter_input_module_compliance_id,
        filter_input_module_title,
        ComOblParmeter


    )






    def get_compliance_benchmark(self,obj):
        if obj.compliance_benchmark:
            return str(obj.compliance_benchmark)+"%"
        else:
            return "0%"

    def get_compliance_id(self, obj):
        if obj.input_framing_module:
            return obj.input_framing_module.unique_id

    def get_compliance_title(self, obj):
        if obj.input_framing_module:
            return obj.input_framing_module.title





    def get_receive_date(self, obj):
        if int(self.user.user_type) < 2:
            if obj.receive_date:
                return obj.receive_date
        elif int(self.user.user_type) > 1:
            return obj.create_date
    



    get_receive_date.short_description = 'receive date'
    get_compliance_id.short_description = 'Compliance ID'
    get_compliance_title.short_description = 'Compliance Title'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        current_category = request.user.user_type
        compliance_owner = request.user.compliance_owner

        if current_category == '1':
            return qs.filter(objects_s1tatus='2')
        elif current_category == '2':
             return qs.filter(compliance_owner_function__id=compliance_owner.id,
                             objects_status='2')
        elif current_category == '3':
            return qs.filter(compliance_owner_function__id=compliance_owner.id,
                             functional_SPOC=request.user, objects_status='1', create_date__lte=datetime.now().date())
        elif current_category == '4':
            return qs.filter(compliance_owner_function_id=compliance_owner,
                             functional_SPOC=request.user, objects_status='1', create_date__lte=datetime.now().date())
        return qs

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}


        if request.user.user_type != '1':
            self.readonly_fields = ["input_framing_module", "get_compliance_id",
                       "get_compliance_benchmark", "compliance_owner_function",
                       "compliance_statement", "compliance_id","compliance_question", 'Get_unique_id', 'get_benchmark', 'manager_comment']

        else:
            self.readonly_fields = ["input_framing_module", "get_compliance_id",
                       "get_compliance_benchmark", "compliance_owner_function",
                       "compliance_statement", "compliance_id","compliance_question", 'Get_unique_id', 'get_benchmark']


        return super(InputModuleAdmin, self).change_view(
            request, object_id, form_url, extra_context=extra_context,
        )

    def changelist_view(self, request, extra_context=None):

        if InputModule.objects.all() is not None:
            datas = InputModule.objects
            user = request.user
            if user.user_type == '1':
                datas = datas.all()
            elif user.user_type == '2':
                user_division = user.compliance_owner
                datas = datas.filter(compliance_owner_function=user_division)
            elif user.user_type == '3' or user.user_type == '4':
                datas = datas.filter(functional_SPOC=user)


            extra_context = {
                'pending': datas.filter(objects_status=1).count(),
                'responder': datas.filter(objects_status=2).count()
            }

        setattr(self, 'user', request.user)
        return super(InputModuleAdmin, self).changelist_view(
            request, extra_context)


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'compliance_owner', 'user_type')


class InputFramingModuleInlineAdmin(admin.ModelAdmin):

    pass

class AuditModuleAdmin(admin.ModelAdmin):
    inlines = [AuditUploadInline]


    list_display = ('profile_link', 'name')

    list_filter = (
        ('name', DropdownFilter),

    )

class DocumentRepositoryModuleAdmin(admin.ModelAdmin):
    inlines = [DocumentRepositoryUploadsUploadInline]


    list_display = ('profile_link', 'name')

    list_filter = (
        ('name', DropdownFilter),

    )

 

class PolicyAdvocacyAdmin(admin.ModelAdmin):
    inlines = [PolicyAdvocacyInline]

    list_display = ('profile_link', 'name')




        

admin.site.register(ComplianceCategory)
admin.site.register(Type)
admin.site.register(InputFramingModule, InputFramingModuleAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(ComplianceOwner)
admin.site.register(InputFramingModuleInlineInformation, InputFramingModuleInlineAdmin)
admin.site.register(InputModule, InputModuleAdmin)
admin.site.register(QuarterOnQuarter)
admin.site.register(AuditReport,AuditModuleAdmin)
admin.site.register(AuditUploads)
admin.site.register(NewDirectiveCirculation,NewDirectiveCirculationAdmin)
admin.site.register(NewDirectiveCirculationInlineInformation)
admin.site.register(ResponderInputPage)
admin.site.register(NewDirInline)


admin.site.register(DocumentRepository,DocumentRepositoryModuleAdmin)
admin.site.register(DocumentRepositoryUploads)

admin.site.register(PolicyAdvocacy,PolicyAdvocacyAdmin)
admin.site.register(PolicyAdvocacyUploads)


admin.site.site_header = "Compliance Automation Admin"
admin.site.site_title = "Compliance Automation Portal"
admin.site.index_title = "Welcome to Compliance Automation Portal"
