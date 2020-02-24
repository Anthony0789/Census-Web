from bottle import run, request, post, get
import time
import json

host = "localhost"
port = "8081"
# -----------------------------------API calls---------------------------------------------
@post('/api/register_write')
def register_write():
    user_name = request.POST.get('user_name')
    email = request.POST.get('email')
    password = request.POST.get('password')
    user_type = request.POST.get('user_type')
    file_obj = open("data/users.data", 'r+')
    lines = file_obj.readlines()
    last_data = lines[-1]
    last_id = int(last_data.split(' ')[0])
    user_id = last_id + 1
    file_obj.write(str(user_id)+' '+user_name+' '+email+' '+password+' '+str(user_type)+'\n')
    file_obj.close()
    return {'user_id':user_id, 'user_name':user_name}

@post('/api/check_register')
def check_register():
    email = request.POST.get('email')
    file_obj = open("data/users.data")
    login_string = ""
    for lines in file_obj:
        user_info = lines.split(' ')
        if email == user_info[2]:
            login_string ="This email has been registered"
            file_obj.close()
            return {'message':login_string, 'result':False}
    login_string = 'Registered successfully'
    file_obj.close()
    return {'message':login_string, 'result':True}

@post('/api/check_login')
def login_check():
    email = request.POST.get('email')
    password = request.POST.get('password')
    file_obj = open("data/users.data", 'r')
    for lines in file_obj:
        user_info = lines.split(' ')
        if email == user_info[2] and password == user_info[3]:
            file_obj.close()
            return {'result':True, 'user_id':user_info[0], 'user_name':user_info[1], 'email':user_info[2], 'user_type':user_info[4]}
    file_obj.close()
    return {'result':False}

@post('/api/details_change')
def details_change():
    user_id = request.POST.get('user_id')
    new_user_name = request.POST.get('new_name')
    old_password = request.POST.get('old_password')
    new_password = request.POST.get('new_password')
    file_obj = open("data/users.data", 'r+')
    new_lines = []
    is_success = False
    for lines in file_obj:
        user_info = lines.split(' ')
        if user_id == user_info[0] and old_password == user_info[3]:
            new_info = user_info[0]+" "+new_user_name+" "+user_info[2]+" "+new_password+" "+user_info[4]
            new_lines.append(new_info)
            is_success = True
        else:
            new_lines.append(lines)
    file_obj.close()
    file_obj = open("data/users.data", 'w')
    for lines in new_lines:
        file_obj.write(lines)
    file_obj.close()
    return {'result':is_success}

#survey write form: user_id ans1 ans2 ans3 ans4 ans5 ans6 comple_num comple_status
@post('/api/survey_write')
def survey_write():
    user_id = request.POST.get('user_id')
    survey = json.loads(request.POST.get('survey'))
    file_obj = open("data/survey.data", 'a+')
    file_obj.write(str(user_id)+' ')
    num = len(survey)
    count = 0
    for i in survey:
        count += 1
        if count != num:
            file_obj.write(str(i)+' ')
        else:
            file_obj.write(str(i)+'\n')
    file_obj.close()

@post('/api/survey_read')
def survey_read():
    user_id = request.POST.get('user_id')
    file_obj = open("data/survey.data", 'r')
    for lines in file_obj:
        survey = lines.split(' ')
        if str(user_id) == survey[0]:
            file_obj.close()
            return {'result':True, 'survey':survey}
    file_obj.close()
    return {'result':False}

@post('/api/survey_view_completion')
def survey_view_completion():
    file_obj = open("data/survey.data", 'r')
    result = []
    for lines in file_obj:
        survey = lines.split(' ')
        user_complete = [survey[0], survey[7]]
        result.append(user_complete)
    file_obj.close()
    return {'result':result}

@post('/api/survey_statics')
def survey_statics():
    count_ans = [[0, 0, 0, 0, 0, 0, 0],[0, 0],[0, 0, 0, 0, 0, 0, 0],[0, 0, 0, 0, 0, 0],[0, 0, 0, 0, 0, 0],[0, 0, 0]]
    count_num = [0.0, 0.0 ,0.0 ,0.0 ,0.0 ,0.0]
    file_obj = open("data/survey.data", 'r')
    for line in file_obj:
        data_line = line.split(' ')
        if data_line[1] == "lower_than_12":
            count_ans[0][0] += 1
            count_num[0] += 1
        elif data_line[1] == "12-18":
            count_ans[0][1] += 1
            count_num[0] += 1
        elif data_line[1] == "19-32":
            count_ans[0][2] += 1
            count_num[0] += 1
        elif data_line[1] == "33-48":
            count_ans[0][3] += 1
            count_num[0] += 1
        elif data_line[1] == "49-60":
            count_ans[0][4] += 1
            count_num[0] += 1
        elif data_line[1] == "61-75":
            count_ans[0][5] += 1
            count_num[0] += 1
        elif data_line[1] == "Over75":
            count_ans[0][6] += 1
            count_num[0] += 1

        if data_line[2] == "male":
            count_ans[1][0] += 1
            count_num[1] += 1
        elif data_line[2] == "female":
            count_ans[1][1] += 1
            count_num[1] += 1

        if data_line[3] == "NSW":
            count_ans[2][0] += 1
            count_num[2] += 1
        elif data_line[3] == "QLD":
            count_ans[2][1] += 1
            count_num[2] += 1
        elif data_line[3] == "SA":
            count_ans[2][2] += 1
            count_num[2] += 1
        elif data_line[3] == "WA":
            count_ans[2][3] += 1
            count_num[2] += 1
        elif data_line[3] == "VAC":
            count_ans[2][4] += 1
            count_num[2] += 1
        elif data_line[3] == "TAC":
            count_ans[2][5] += 1
            count_num[2] += 1
        elif data_line[3] == "Overseas":
            count_ans[2][6] += 1
            count_num[2] += 1

        if data_line[4] == "NSW":
            count_ans[3][0] += 1
            count_num[3] += 1
        elif data_line[4] == "QLD":
            count_ans[3][1] += 1
            count_num[3] += 1
        elif data_line[4] == "SA":
            count_ans[3][2] += 1
            count_num[3] += 1
        elif data_line[4] == "WA":
            count_ans[3][3] += 1
            count_num[3] += 1
        elif data_line[4] == "VAC":
            count_ans[3][4] += 1
            count_num[3] += 1
        elif data_line[4] == "TAC":
            count_ans[3][5] += 1
            count_num[3] += 1

        if data_line[5] == "Less_than_one_month":
            count_ans[4][0] += 1
            count_num[4] += 1
        elif data_line[5] == "One_to_six_month":
            count_ans[4][1] += 1
            count_num[4] += 1
        elif data_line[5] == "Six_to_twelve_month":
            count_ans[4][2] += 1
            count_num[4] += 1
        elif data_line[5] == "Over_a_year":
            count_ans[4][3] += 1
            count_num[4] += 1
        elif data_line[5] == "Longer_than_3_years":
            count_ans[4][4] += 1
            count_num[4] += 1
        elif data_line[5] == "Never_leaved":
            count_ans[4][5] += 1
            count_num[4] += 1

        if data_line[6] == "No":
            count_ans[5][0] += 1
            count_num[5] += 1
        elif data_line[6] == "Yes,Aboriginal":
            count_ans[5][1] += 1
            count_num[5] += 1
        elif data_line[6] == "Yes,Torres_Strait_Islander":
            count_ans[5][2] += 1
            count_num[5] += 1
    file_obj.close()

    for i in range(len(count_ans)):
        for j in range(len(count_ans[i])):
            if count_num[i] != 0:
                count_ans[i][j] = round(count_ans[i][j]/count_num[i], 4) * 100
            else:
                count_ans[i][j] = round(0, 4) * 100

    return {'result':count_ans}

@post('/api/application_write')
def application_write():
    user_id = request.POST.get('user_id')
    user_name = request.POST.get('user_name')
    file_obj = open("data/application.data", 'a+')
    application_info = str(user_id)+" "+user_name+"\n"
    file_obj.write(application_info)
    file_obj.close()

@post('/api/application_search')
def application_search():
    user_id = request.POST.get('user_id')
    file_obj = open("data/application.data", 'r')
    for lines in file_obj:
        application = lines.split(" ")
        if application[0] == str(user_id):
            file_obj.close()
            return {'result':True}
    file_obj.close()
    return {'result':False}

@post('/api/application_read')
def application_read():
    file_obj = open("data/application.data", 'r')
    result_list = []
    for lines in file_obj:
        application = lines.split(" ")
        application[0] = int(application[0])
        result_list.append(application)
    file_obj.close()
    return {'result':result_list}

@post('/api/application_approve')
def application_approve():
    user_id = request.POST.get('user_id_request')
    #delete data in survey.data
    file_obj_survey = open("data/survey.data")
    new_survey = []
    for lines in file_obj_survey:
        survey = lines.split(' ')
        if user_id != survey[0]:
            new_survey.append(lines)
    file_obj_survey.close()
    file_obj_survey = open("data/survey.data", 'w')
    if len(new_survey) == 0:
        file_obj_survey.write("")
    else:
        for lines in new_survey:
            file_obj_survey.write(lines)
    file_obj_survey.close()
    #delete data in application.data
    file_obj_application = open("data/application.data")
    new_application = []
    for lines in file_obj_application:
        application = lines.split(' ')
        if user_id != application[0]:
            new_application.append(lines)
    file_obj_application.close()
    file_obj_application = open("data/application.data", 'w')
    if len(new_application) == 0:
        file_obj_application.write("")
    else:
        for lines in new_application:
            file_obj_application.write(lines)
    file_obj_application.close()

@post('/api/log')
def log():
    user_id = request.POST.get('user_id')
    user_name = request.POST.get('user_name')
    action = request.POST.get('action')
    file_obj = open("data/log.data", 'a+')
    time_info = time.strftime('%Y-%m-%d %H:%M',time.localtime(time.time()))
    log_info = time_info+" user_id:"+str(user_id)+" username:"+user_name+" "+action+"\n"
    file_obj.write(log_info)
    file_obj.close()

@post('/api/view_log')
def view_log():
    file_obj = open("data/log.data", 'r')
    lines = file_obj.readlines()
    file_obj.close()
    return {'result':lines}

@post('/api/clear_all_data')
def clear_all_data():
    #clear users file
    file_obj_users = open("data/users.data", 'w')
    file_obj_users.write('1 admin admin 8a5b54ddd365b1576d6f80af8c7dc14c88eaee574070574fbcd0e62678c27d46 3'+'\n')
    file_obj_users.close()
    #clear survey file_obj
    file_obj_survey = open("data/survey.data", 'w')
    file_obj_survey.write('')
    file_obj_survey.close()
    #clear log file_obj
    file_obj_application = open("data/application.data", 'w')
    file_obj_application.write('')
    file_obj_application.close()
    #clear log file_obj
    file_obj_log = open("data/log.data", 'w')
    file_obj_log.write('')
    file_obj_log.close()

run(host=host, port=port)
