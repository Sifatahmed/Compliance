from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

# Create your models here.

class Meta:
    app_label = 'compliance_digitalization_app'

class ComplianceOwner(models.Model):
    name = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return self.name

class User(AbstractUser):
    type= (
        ('1', 'Category 1'),
        ('2', 'Category 2'),
        ('3', 'Category 3'),
        ('4', 'Category 4')
    )
    user_type=models.CharField(max_length=20,choices=type,blank=True)
    compliance_owner = models.ForeignKey(ComplianceOwner, null=True, blank=False, on_delete=models.CASCADE)
    original_pass = None

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self.original_pass = self.password

    def save(self, *args, **kwargs):


        if not self.user_type:
            self.user_type='4'

        if self._state.adding:
            if self.compliance_owner:
                self.set_password(self.password)
                self.is_staff = True
            else:
                self.password = self.password
        else:
            if self.password != self.original_pass:
                self.set_password(self.password)

            else:
                pass

        super(User, self).save(*args, **kwargs)
        self.original_pass = self.password

        
        # if not self.user_type:
        #     self.user_type='4'

        # if self._state.adding:
        #     if self.compliance_owner:
        #         self.set_password(self.password)
        #         self.is_staff = True

        #         if self.user_type > '1':

        #             input_type = ContentType.objects.get_for_model(InputModule, for_concrete_model=True)
        #             mitigation_type = ContentType.objects.get_for_model(MitigationPlan, for_concrete_model=True)


        #             input_module_permissions = Permission.objects.filter(content_type=input_type)


        #             mitigation_plan_permissions = Permission.objects.filter(content_type=mitigation_type)

        #             for i, m in zip(input_module_permissions, mitigation_plan_permissions):
                       
        #                 self.user_permissions.add(i)
        #                 self.user_permissions.add(m)

        #         else:
        #             self.is_superuser = True

        #     else:
        #         self.password = self.password
        # else:
        #     if self.password != self.original_pass:
        #         self.set_password(self.password)

        #         if self.user_type > '1':

        #             input_type = ContentType.objects.get_for_model(InputModule, for_concrete_model=True)
        #             mitigation_type = ContentType.objects.get_for_model(MitigationPlan, for_concrete_model=True)


        #             input_module_permissions = Permission.objects.filter(content_type=input_type)


        #             mitigation_plan_permissions = Permission.objects.filter(content_type=mitigation_type)

        #             for i, m in zip(input_module_permissions, mitigation_plan_permissions):
                       
        #                 self.user_permissions.add(i)
        #                 self.user_permissions.add(m)

        #         else:
        #             self.is_superuser = True

            

        #     else:




        #         if self.user_type > '1':


        #             input_type = ContentType.objects.get_for_model(InputModule, for_concrete_model=True)
        #             mitigation_type = ContentType.objects.get_for_model(MitigationPlan, for_concrete_model=True)


        #             input_module_permissions = Permission.objects.filter(content_type=input_type)


        #             mitigation_plan_permissions = Permission.objects.filter(content_type=mitigation_type)

        #             for i, m in zip(input_module_permissions, mitigation_plan_permissions):

                       
        #                 # self.user_permissions.add(m)
        #                 # self.user_permissions.add(i)
        #                 self.is_superuser = False

        #                 self.user_permissions.set([1, 2, 20])



        #                 print(self.user_permissions.all())
                      
                        
                        

        #         else:
        #             print('superuser')
        #             self.is_superuser = True




        # super(User, self).save(*args, **kwargs)
        # self.original_pass = self.password


class ComplianceCategory(models.Model):
    name = models.CharField(max_length=120)
    def __unicode__(self):
        return self.name
    def __str__(self):
        return self.name


class Type(models.Model):
    name = models.CharField(max_length=120)



class InputFramingModule(models.Model):
    unique_id = models.CharField( null=True, blank=True, max_length=100)
    title = models.TextField(null=True, blank=False, verbose_name='Compliance Statement')
    benchmark = models.CharField(max_length=30, null=True, blank=True)
    source_of_obligation= models.TextField( null=True, blank=False)
    clause_no= models.CharField(max_length=30, null=True, blank=False)
    _type = (
        ('1', 'Major'),
        ('2', 'Non Major')
    )
    Requirement=(
        ('1', 'Yes/No Statement only'),
        ('2', 'Yes/No + % Value'),
        ('3', 'Yes/No + Number'),
        ('4', 'Yes/No + Date'),
    )
    type=models.CharField(max_length=20,choices=_type,blank=False,null=True)
    compliance_category = models.ForeignKey(ComplianceCategory,blank=False,null=True, on_delete=models.CASCADE)
    Input_Requirement=models.CharField(max_length=20,choices=Requirement,blank=False,null=True)

    proof_of_compliance = models.BooleanField(default=False, blank=True)     
    attachment = models.FileField(upload_to='%Y/%m/%d', null=True, blank=True)
    question_note_to_SPOC = models.TextField(blank=True, null=True, verbose_name='Question/Note To SPOC')

    def Get_unique_id(self):
        return  str(self.id)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):        

        if self._state.adding:
           pass

        else:

            filter_input = InputModule.objects.filter(input_framing_module=self.id).last()
               
            filter_input.proof_of_compliance = self.attachment
            filter_input.save()
        
        super(InputFramingModule, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        attachment.delete()

        super(InputFramingModule, self).delete(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Compliance Framing Modules'

class InputFramingModuleInlineInformation(models.Model):
    type= (
    ('1', 'Yes'),
    ('2', 'No'),
    )

    assessment_frequencys=(
        ("1","Daily"),
        ("2","Weekly"),
        ("3","Fortnightly"),
        ("4","Monthly"),
        ("5","Bi-monthly"),
        ("6","Quarterly"),
        ("7","Half-yearly"),
        ("8","Yearly"),
        ("9","As and when required"),
        ("10","Daily checking"),
        ("11","Weekly checking"),
        ("12","Quarterly checking"),
        ("13","Yearly checking"),
        )

    notification_number=(
    ("1","1"),
    ("2","2"),
    ("3","3"),
    ("4","4"),
    ("5","5"),
    ("6","6"),
    ("7","7"),
    ("8","8"),
    ("9","9"),
    ("10","10"),
    ("11","11"),
    ("12","12"),
    ("13","13"),

    ("14","14"),
    ("15","15"),
    ("16","16"),
    ("17","17"),
    ("18","18"),
    ("19","19"),
    ("20","20"),
    ("21","21"),
    ("22","22"),
    ("23","23"),
    ("24","24"),
    ("25","25"),
    ("26","26"),
    ("27","27"),
    ("28","28"),
    ("29","29"),
    ("30","30"),
    )
    compliance_owner_function = models.ForeignKey(ComplianceOwner, on_delete=models.CASCADE, null=True)
    functional_SPOC = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    email_of_SPOC = models.EmailField(max_length=100, blank=False)
    LM_of_SPOC = models.CharField(max_length=120, blank=False, null=True)
    email_of_SPOC_LM = models.EmailField(max_length=100, blank=False)
    assessment_date = models.DateField(blank=False, null=True)
    assessment_frequency = models.CharField(max_length=120, blank=False,choices=assessment_frequencys, null=True)
    prior_notification = models.CharField(max_length=120, blank=False, null=True, choices=notification_number)
    reminder_notification = models.CharField(max_length=120, blank=False, null=True, choices=notification_number)
    escalation_notification = models.CharField(max_length=120, blank=False, choices= type, null=True)
    InputFramingModule_id = models.ForeignKey(InputFramingModule, on_delete=models.CASCADE, null=True)
    input_module_id = models.IntegerField(blank=True,null=True)

    def __str__(self):
        return self.compliance_owner_function.name

    def save(self, *args, **kwargs):
        if self.pk is None:
            input_module = InputModule()
            input_module.input_framing_module = self.InputFramingModule_id
            # input_module.compliance_id = self.InputFramingModule_id.unique_id
            input_module.compliance_statement = self.InputFramingModule_id.title
            input_module.compliance_benchmark = self.InputFramingModule_id.benchmark
            input_module.compliance_owner_function= self.compliance_owner_function
            input_module.functional_SPOC= self.functional_SPOC
            input_module.objects_status= 1
            input_module.compliance_question =self.InputFramingModule_id.question_note_to_SPOC
            input_module.FramingInline_id = self.pk

            if self.InputFramingModule_id.attachment:
                input_module.proof_of_compliance = self.InputFramingModule_id.attachment
            

            if self.assessment_date == datetime.now().date():
                input_module.create_date = datetime.now().date()

            elif  self.assessment_date > datetime.now().date():
                input_module.create_date = self.assessment_date

            else:

                input_module.create_date = self.assessment_date


            
            input_module.save()
            self.input_module_id = input_module.id

        else:
            input_module = InputModule.objects.get(id=self.input_module_id)
            input_module.compliance_owner_function = self.compliance_owner_function
            input_module.functional_SPOC= self.functional_SPOC
            input_module.compliance_statement = self.InputFramingModule_id.title
            input_module.compliance_benchmark = self.InputFramingModule_id.benchmark

            if self.assessment_date == datetime.now().date():
                input_module.create_date = datetime.now().date()

            elif  self.assessment_date > datetime.now().date():
                input_module.create_date = self.assessment_date

            else:

                input_module.create_date = self.assessment_date

            input_module.save()

            print(input_module.compliance_owner_function , input_module.functional_SPOC, input_module.id)

        
        super(InputFramingModuleInlineInformation, self).save(*args, **kwargs)


class InputModule(models.Model):
    status = (
        ('1', 'Yes'),
        ('2', 'No'),
        )

    imporve_status = (
        ('1', 'Pending'),
        ('2', 'Responded')
    )


    FramingInline_id =models.ForeignKey(InputFramingModuleInlineInformation, on_delete=models.CASCADE,blank=False,null=True)
    input_framing_module = models.ForeignKey(InputFramingModule, on_delete=models.CASCADE,blank=False, null=True)
    compliance_id = models.CharField(blank=True, max_length=100)
    compliance_statement = models.CharField(max_length=30, blank=True)
    compliance_benchmark = models.CharField(max_length=30, blank=True,null=True)
    compliance_question = models.TextField(blank=True, null=True)
    proof_of_compliance = models.FileField(upload_to='%Y/%m/%d', blank=True,null=True)
    current_status = models.CharField(max_length=120, blank=False, choices= status)
    percentage_rate = models.FloatField(max_length=120, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    number = models.IntegerField(blank=True, null=True)
    user_comment = models.TextField(blank=True, null=True)
    manager_comment = models.TextField(blank=True, null=True)

    # mitigation_plan = models.FileField(upload_to='/%Y/%m/%d', blank=True)
    mitigation_plan_Statement = models.CharField(max_length=120, blank=True,null=True)
    root_cause = models.TextField(max_length=2000, blank=True)
    target_date_of_closure = models.DateField(blank=True, null=True)
    mitigation_plan_validated_by = models.CharField(max_length=120, blank=True)
    objects_status = models.CharField(max_length=120, blank=True, choices= imporve_status)
    compliance_owner_function = models.ForeignKey(ComplianceOwner, on_delete=models.CASCADE, null=True)
    functional_SPOC = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    receive_date = models.DateField(blank=True, null=True)
    create_date = models.DateField(null=True, blank=True)

    changed_file = models.BooleanField(default=False, blank=True)     




    





    def __str__(self):
        return self.input_framing_module.title
    class Meta:
        verbose_name_plural = 'Compliance Modules'
    def Get_unique_id(self):
        if self.input_framing_module:
            return  str(self.input_framing_module.id )


    def get_benchmark(self):
        if self.input_framing_module.benchmark:


            return self.input_framing_module.benchmark

        else:
            return ''
    get_benchmark.short_description = 'benchmark'

class MitigationPlan(models.Model):
    Title =models.CharField(max_length=300, blank=True)
    file = models.FileField(upload_to='%Y/%m/%d', blank=True)
    input_module = models.ForeignKey(InputModule, on_delete=models.CASCADE, blank=False, null=True)



class QuarterOnQuarter(models.Model):
    YearMonth = models.DateField(blank=False, null=False)
    CompliancePercentage = models.FloatField(max_length=10, null=False, blank=False)
    NonCompliancePercentage = models.FloatField(max_length=10, null=False, blank=False)
    freeze = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.YearMonth.strftime('%B')+' '+self.YearMonth.strftime('%Y')
    class Meta:
        verbose_name_plural = 'QOQ'

#class Test(models.Model):
#    Title =models.CharField(max_length=300, blank=True)

class AuditReport(models.Model):
    name = models.CharField(max_length=250)



    def __str__(self):
        if self.name:
            return self.name

    def profile_link(self):
        return '%s' % (self.id)
    profile_link.allow_tags = True
    profile_link.short_description = 'Folder ID'

class AuditUploads(models.Model):
    Title = models.CharField(max_length=300, blank=True)
    file = models.FileField(upload_to='%Y/%m/%d', blank=True)
    input_audit = models.ForeignKey(AuditReport, on_delete=models.CASCADE, blank=False, null=True)




    def __str__(self):
        if self.Title:

            return self.Title


class DocumentRepository(models.Model):
    name = models.CharField(max_length=250)



    def __str__(self):
        if self.name:
            return self.name

    def profile_link(self):
        return '%s' % (self.id)
    profile_link.allow_tags = True
    profile_link.short_description = 'Folder ID'

class DocumentRepositoryUploads(models.Model):
    Title = models.CharField(max_length=300, blank=True)
    file = models.FileField(upload_to='%Y/%m/%d', blank=True)
    input_audit = models.ForeignKey(DocumentRepository, on_delete=models.CASCADE, blank=False, null=True)




    def __str__(self):
        if self.Title:

            return self.Title



class PolicyAdvocacy(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name

    def profile_link(self):
        return '%s' % (self.id)
    profile_link.allow_tags = True
    profile_link.short_description = 'Folder ID'

class PolicyAdvocacyUploads(models.Model):
    Title = models.CharField(max_length=300, blank=True)
    file = models.FileField(upload_to='%Y/%m/%d', blank=True)
    input_policy = models.ForeignKey(PolicyAdvocacy, on_delete=models.CASCADE, blank=False, null=True)

    def __str__(self):
        return self.Title



class NewDirectiveCirculation(models.Model):
    directive_name = models.CharField(null=True, blank=False,max_length=100) 

    def __str__(self):
        if self.directive_name:
            return self.directive_name   

        else:
            return ''


class NewDirInline(models.Model):
    upload_file = models.FileField(upload_to='%Y/%m/%d', null=True, blank=True)
    elements_to_be_complied = models.CharField(null=True, blank=True, max_length=100)
    deadline= models.DateField(blank=True, null=True)
    line_item =  models.IntegerField(blank=True,null=True, default=0)
    new_dir_cir = models.ForeignKey(NewDirectiveCirculation, on_delete=models.CASCADE, null=True)
    imporve_status = (
        ('1', 'Pending'),
        ('2', 'Complete')
    )
    current_status = models.CharField(max_length=120, blank=True, choices= imporve_status, null=True)
    implementation_date = models.DateField(blank=True, null=True)
    proof_of_compliance = models.FileField(upload_to='%Y/%m/%d', null=True, blank=True)
    
    def save(self, *args, **kwargs):
        filter_new_dir_obj = NewDirInline.objects.filter(new_dir_cir=self.new_dir_cir)

        if self._state.adding:
            self.current_status = 1
        if filter_new_dir_obj and self.line_item == 0:
            print('exit')
            self.line_item = filter_new_dir_obj.count() + 1

        elif self.line_item == 0:
            print('new')
            self.line_item = 1
            self.current_status = 1

        super(NewDirInline, self).save(*args, **kwargs) 

# This Method will not change

    def __str__(self):
        return str(self.line_item)


class NewDirectiveCirculationInlineInformation(models.Model):
    item = (
    ('1', 'Yes'),
    ('2', 'No'),
)


    line_number=(
    ("1","1"),
    ("2","2"),
    ("3","3"),
    ("4","4"),
    ("5","5"),
    ("6","6"),
    ("7","7"),
    ("8","8"),
    ("9","9"),
    ("10","10"),
    ("11","11"),
    ("12","12"),
    ("13","13"),

    ("14","14"),
    ("15","15"),
    ("16","16"),
    ("17","17"),
    ("18","18"),
    ("19","19"),
    ("20","20"),
    ("21","21"),
    ("22","22"),
    ("23","23"),
    ("24","24"),
    ("25","25"),
    ("26","26"),
    ("27","27"),
    ("28","28"),
    ("29","29"),
    ("30","30"),
    )
    line_item = models.CharField(null=True, blank=True, max_length=100)
    directive_owner_function = models.ForeignKey(ComplianceOwner, on_delete=models.CASCADE, null=True)
    functional_SPOC = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    email_of_SPOC = models.EmailField(max_length=100, blank=False)
    LM_of_SPOC = models.CharField(max_length=120, blank=False, null=True)
    email_of_SPOC_LM = models.EmailField(max_length=100, blank=False)
    assessment_date = models.DateField(blank=False, null=True)
    prior_notification = models.CharField(max_length=120, blank=False, null=True, choices=line_number)
    reminder_notification =models.CharField(max_length=120, blank=False, null=True, choices=line_number)
    escalation_notification = models.CharField(max_length=120, blank=False, choices= item, null=True)
    line_num = models.ForeignKey(NewDirectiveCirculation, on_delete=models.CASCADE, null=True)



class ResponderInputPage(models.Model):
    directive_id = models.CharField(null=True, blank=True, max_length=100)
    directive_statement = models.TextField(null=True, blank=False)
    elements_to_be_complied= models.ForeignKey(ComplianceCategory,blank=False,null=True, on_delete=models.CASCADE)
    deadline = models.DateField(blank=True, null=True)
    implementation_date = models.DateField(blank=True, null=True)
    proof_of_completion = models.FileField(upload_to='%Y/%m/%d', null=True, blank=True)





        

