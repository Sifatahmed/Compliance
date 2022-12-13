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
               'Input Requirement','Question Note to SPOC','Compliance Performance','COMPLIANCE OWNER FUNCTION',
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

            input_obj = InputModule.objects.filter(id=row.input_module_id)

            if input_obj:
                input_obj = input_obj[0]



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
                ws.write(row_num, 11, row.InputFramingModule_id.compliance_performance, font_style)
                ws.write(row_num, 12, row.compliance_owner_function.name, font_style)
                ws.write(row_num, 13, row.functional_SPOC.username, font_style)
                ws.write(row_num, 14, row.email_of_SPOC, font_style)
                ws.write(row_num, 15, row.LM_of_SPOC, font_style)
                ws.write(row_num, 16, row.email_of_SPOC_LM, font_style)
                ws.write(row_num, 17, row.assessment_date, font_style)
                ws.write(row_num, 18, row.get_assessment_frequency_display(), font_style)
                ws.write(row_num, 19, row.get_prior_notification_display(), font_style)
                ws.write(row_num, 20, row.get_reminder_notification_display(), font_style)
                ws.write(row_num, 21  , row.get_escalation_notification_display(), font_style)


    wb.save(response)
    return response