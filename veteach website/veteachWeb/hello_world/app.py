# import boto3
import datetime
import json

# import requests
import requests

import html
# import mysql.connector
# from flask_restful import reqparse
# from flask import render_template
# import os
# import requests
# import operator
# import re
# import nltk
# from flask import Flask, render_template, request
# from flask_sqlalchemy import SQLAlchemy
# from stop_words import stops
# from collections import Counter
# from bs4 import BeautifulSoup
import boto3
import pystache
from boto3.dynamodb.conditions import Key, Attr
from dynamodb_json import json_util as util
from flask_lambda import FlaskLambda
# from flask import request
import razorpay
import uuid

# import numpy as np

global dynamodb
global user_login_status, university_id, university_name, branch_id, branch_name, semester_id, semester_status, branch_status, university_status
global cookies
global user_id, name, email, phone, university_name_cookie, branch_name_cookie, semester_name_cookie, datentime


def fetch_university_query(university_id, offset2, offset3, offset4):
    global response
    table = dynamodb.Table('university')
    if university_id == 0:
        response = table.scan()
    else:
        response = table.query(
            KeyConditionExpression=Key('university_id').eq(int(university_id))
        )
    return response


# if university id is 0 = fetch everything else fetch only the defined university id values
# if return_type is 1 = return <option> else if 2 = return university name else return array
def fetch_university(university_id, return_type, offset1, offset2):
    global detailsarray
    json_value = fetch_university_query(university_id, 0, 0, 0)
    decode_items = util.loads(json_value)
    count = decode_items['Count']
    items = decode_items['Items']
    university_id = []
    university_name = []
    datantime = []
    detailsarray = []
    print_option = ""
    university_name_temp = ""
    university_array = []
    if return_type == 1:
        for i in range(0, count):
            university_array.append(
                "<option value=" + str(util.loads(items[i])['university_id']) + ">" + util.loads(items[i])[
                    'university_name'] + "</option>")
        return university_array
    elif return_type == 2:
        return util.loads(items[0])['university_name']
    else:
        for i in range(0, count):
            university_id.append(util.loads(items[i])['university_id'])
            university_name.append(util.loads(items[i])['university_name'])
            datantime.append(util.loads(items[i])['datantime'])

    detailsarray.append(university_id)
    detailsarray.append(university_name)
    detailsarray.append(datantime)

    return detailsarray


def display_regulation():
    for i in range(10, 22):
        print("<option value='" + str(i) + "'>R" + str(i) + "</option>")


def display_branch():
    branch_array = []
    branch_array.append('<option value="0">ALL</option>')
    branch_array.append('<option value="1">ECE</option>')
    branch_array.append('<option value="2">CSE</option>')
    branch_array.append('<option value="3">EEE</option>')
    branch_array.append('<option value="4">CIVIL</option>')
    branch_array.append('<option value="5">MECH</option>')
    return branch_array


def fetch_branch_name(branch_id):
    switcher = {
        0: "ALL",
        1: "ECE",
        2: "CSE",
        3: "EEE",
        4: "CIVIL",
        5: "MECH"
    }
    return switcher.get(int(branch_id), "")


def display_semester():
    semester_array = []
    semester_array.append('<option value="1">Semester 1</option>')
    semester_array.append('<option value="2">Semester 2</option>')
    semester_array.append('<option value="3">Semester 3</option>')
    semester_array.append('<option value="4">Semester 4</option>')
    semester_array.append('<option value="5">Semester 5</option>')
    semester_array.append('<option value="6">Semester 6</option>')
    semester_array.append('<option value="7">Semester 7</option>')
    semester_array.append('<option value="8">Semester 8</option>')
    return semester_array


def fetch_semester(subject_id, cmd, branch, semester_id, part, university_name, university_id, regulation):
    branch_id = int(branch)
    if cmd == 1 or cmd == 10:  # 1 is old and 10 is new
        if int(part) % 2 == 0:
            semester_id_final = int(semester_id) + int(semester_id)
        else:
            semester_id_final = int(semester_id) + int(semester_id) - 1
        table = dynamodb.Table('subject_v2')
        subject_id_created = str(university_name) + "_" + str(regulation) + "_" + str(branch_id) + "_" + str(
            semester_id_final)
        response = table.query(
            KeyConditionExpression=Key('university_id').eq(str(university_id)) & Key('subject_id').eq(
                str(subject_id_created))
        )

        decode_items = util.loads(response)
        # count = decode_items['Count']
        items = decode_items['Items']
        return items


def fetch_subject_query(subject_id, cmd, branch, semester_id, university_name, university_id, offset4):
    table = dynamodb.Table('subject')
    if cmd == 1:
        # print("**************")
        # print(str(university_name))
        # print("**************")
        # print(int(branch))
        # print("**************")
        # print(int(semester_id))
        # print("**************")
        # response = table.query(
        #     KeyConditionExpression=Key('flag').eq(str("1")) & Key('subject_id').begins_with(str(university_name)),
        #     FilterExpression=Attr('branch_id').eq(str(branch)) & Attr('semester_id').eq(str(semester_id))
        # )
        # response1 = table.query(
        #     KeyConditionExpression=Key('flag').eq(str(2)) & Key('subject_id').begins_with(str(university_name)),
        #     FilterExpression=Attr('branch_id').eq(str(branch)) & Attr('semester_id').eq(str(semester_id))
        # )
        # arr1 = np.array(response['Items'])
        # arr2 = np.array(response1['Items'])
        # final_arr = np.concatenate(arr1,arr2)
        # print(final_arr)
        response = table.scan(
            FilterExpression=Attr('subject_id').begins_with(str(university_name)) & Attr('branch_id').eq(
                str(branch)) & Attr('semester_id').eq(str(semester_id)) & Attr('flag').gt('0')
        )
    elif cmd == 10:
        # table = dynamodb.Table('subject_new')
        table = dynamodb.Table('subject_v2')
        response = table.query(
            KeyConditionExpression=Key('university_id').eq(str("6")) & Key('subject_id').begins_with(
                str(university_name)),
            FilterExpression=Attr('semester_id').contains(str(branch) + "_" + str(semester_id)) & Attr('flag').gt('0')
        )
    elif cmd == 2:
        # response = table.scan(
        #     FilterExpression=Attr('flag').eq(str(2))
        # )
        # print("*******************************")
        # print(str(university_name))
        # print("*******************************")
        response = table.query(
            KeyConditionExpression=Key('flag').eq(str("2")) & Key('subject_id').begins_with(str(university_name))
        )
        # order by prioritykdfsdf
    elif cmd == 106:
        table = dynamodb.Table('subject_v2')
        response = table.query(
            KeyConditionExpression=Key('university_id').eq(str(university_id)) & Key('subject_id').begins_with(str(university_name))
        )
        decode_items = util.loads(response)
        # count = decode_items['Count']
        items = decode_items['Items']
        return items
    else:
        if subject_id == 0:
            response = table.scan()
        else:
            response = table.query(
                KeyConditionExpression=Key('subject_id').eq(str(subject_id))
            )

    return response


# def fetch_subject_purchase_status_query(subject_id,cmd,offset1,offset2):
#     table = dynamodb.Table('')

# cmd 1 is to fetch subject for start learning
# cmd 2 is to fetch subject for home page
# pending*** 1st video id should be included in subject table and return it
def fetch_subject(subject_id, cmd, branch, semester_id, part, university_name, testflag):
    branch_id = int(branch)
    if cmd == 1 or cmd == 10:  # 1 is old and 10 is new
        if int(part) % 2 == 0:
            semester_id_final = int(semester_id) + int(semester_id)
        else:
            semester_id_final = int(semester_id) + int(semester_id) - 1

        if (semester_id_final == 1 or semester_id_final == 2) and cmd != 10:
            branch_id = 0

        json_value = fetch_subject_query(subject_id, cmd, branch_id, semester_id_final, university_name, 0, 0)
    elif cmd == 2:
        json_value = fetch_subject_query(0, cmd, 0, 0, university_name, 0, 0)
    else:
        json_value = fetch_subject_query(subject_id, 0, 0, 0, university_name, 0, 0)

    decode_items = util.loads(json_value)
    count = decode_items['Count']
    items = decode_items['Items']
    if testflag == 1:
        return items

    detailsarray = []
    subject_id_array = []
    university_name_array = []
    regulation_array = []
    semester_name_array = []
    branch_name_array = []
    subject_name_array = []
    professor_name_array = []
    price_array = []
    discounted_price_array = []
    subject_photo_array = []
    tags_array = []
    university_id_array = []
    professor_id_array = []
    branch_id_array = []
    semester_id_array = []
    subject_description_array = []
    subject_flag_array = []
    subject_num_of_units_array = []
    first_video_id_array = []

    unit1_array = []
    unit2_array = []
    unit3_array = []
    unit4_array = []
    unit5_array = []
    unit6_array = []
    unit7_array = []
    unit8_array = []
    unit9_array = []
    unit10_array = []
    unit1_name_array = []
    unit2_name_array = []
    unit3_name_array = []
    unit4_name_array = []
    unit5_name_array = []
    unit6_name_array = []
    unit7_name_array = []
    unit8_name_array = []
    unit9_name_array = []
    unit10_name_array = []

    for i in range(0, count):
        subject_id_array.append(util.loads(items[i])['subject_id'])
        university_name_array.append(fetch_university(util.loads(items[i])['university_id'], 2, 0, 0))
        regulation_array.append("R" + str(util.loads(items[i])['regulation']))
        branch_name_array.append(fetch_branch_name(util.loads(items[i])['branch_id']))
        semester_name_array.append("Semester " + str(util.loads(items[i])['semester_id']))
        subject_name_array.append(util.loads(items[i])['subject_name'])
        try:
            professor_name_array.append(util.loads(items[i])['professor_id'])
        except:
            professor_name_array.append("0")
        price_array.append(util.loads(items[i])['price'])
        discounted_price_array.append(util.loads(items[i])['discounted_price'])
        subject_photo_array.append(util.loads(items[i])['subject_photo'])
        tags_array.append(util.loads(items[i])['tags'])
        university_id_array.append(util.loads(items[i])['university_id'])
        try:
            professor_id_array.append(util.loads(items[i])['professor_id'])
        except:
            professor_id_array.append("0")
        branch_id_array.append(util.loads(items[i])['branch_id'])
        semester_id_array.append(util.loads(items[i])['semester_id'])
        subject_description_array.append(util.loads(items[i])['subject_description'])
        subject_flag_array.append(util.loads(items[i])['flag'])
        subject_num_of_units_array.append(util.loads(items[i])['num_of_unit'])
        try:
            first_video_id_array.append(util.loads(items[i])['first_video_id'])
        except:
            first_video_id_array.append(0)

        try:
            unit1_array.append(util.loads(items[i])['unit1'])
        except:
            unit1_array.append("")
        try:
            unit2_array.append(util.loads(items[i])['unit2'])
        except:
            unit2_array.append("")
        try:
            unit3_array.append(util.loads(items[i])['unit3'])
        except:
            unit3_array.append("")
        try:
            unit4_array.append(util.loads(items[i])['unit4'])
        except:
            unit4_array.append("")
        try:
            unit5_array.append(util.loads(items[i])['unit5'])
        except:
            unit5_array.append("")
        try:
            unit6_array.append(util.loads(items[i])['unit6'])
        except:
            unit6_array.append("")
        try:
            unit7_array.append(util.loads(items[i])['unit7'])
        except:
            unit7_array.append("")
        try:
            unit8_array.append(util.loads(items[i])['unit8'])
        except:
            unit8_array.append("")
        try:
            unit9_array.append(util.loads(items[i])['unit9'])
        except:
            unit9_array.append("")
        try:
            unit10_array.append(util.loads(items[i])['unit10'])
        except:
            unit10_array.append("")
        try:
            unit1_name_array.append(util.loads(items[i])['unit1_name'])
        except:
            unit1_name_array.append("")
        try:
            unit2_name_array.append(util.loads(items[i])['unit2_name'])
        except:
            unit2_name_array.append("")
        try:
            unit3_name_array.append(util.loads(items[i])['unit3_name'])
        except:
            unit3_name_array.append("")
        try:
            unit4_name_array.append(util.loads(items[i])['unit4_name'])
        except:
            unit4_name_array.append("")
        try:
            unit5_name_array.append(util.loads(items[i])['unit5_name'])
        except:
            unit5_name_array.append("")
        try:
            unit6_name_array.append(util.loads(items[i])['unit6_name'])
        except:
            unit6_name_array.append("")
        try:
            unit7_name_array.append(util.loads(items[i])['unit7_name'])
        except:
            unit7_name_array.append("")
        try:
            unit8_name_array.append(util.loads(items[i])['unit8_name'])
        except:
            unit8_name_array.append("")
        try:
            unit9_name_array.append(util.loads(items[i])['unit9_name'])
        except:
            unit9_name_array.append("")
        try:
            unit10_name_array.append(util.loads(items[i])['unit10_name'])
        except:
            unit10_name_array.append("")

    detailsarray.append(subject_id_array)
    detailsarray.append(university_name_array)
    detailsarray.append(regulation_array)
    detailsarray.append(branch_name_array)
    detailsarray.append(semester_name_array)
    detailsarray.append(subject_name_array)
    detailsarray.append(professor_name_array)
    detailsarray.append(price_array)
    detailsarray.append(discounted_price_array)
    detailsarray.append(subject_photo_array)
    detailsarray.append(tags_array)
    detailsarray.append(university_id_array)
    detailsarray.append(professor_id_array)
    detailsarray.append(branch_id_array)
    detailsarray.append(semester_id_array)
    detailsarray.append(subject_description_array)
    detailsarray.append(subject_flag_array)
    detailsarray.append(subject_num_of_units_array)
    detailsarray.append(first_video_id_array)

    detailsarray.append(unit1_name_array)
    detailsarray.append(unit1_array)

    detailsarray.append(unit2_name_array)
    detailsarray.append(unit2_array)

    detailsarray.append(unit3_name_array)
    detailsarray.append(unit3_array)

    detailsarray.append(unit4_name_array)
    detailsarray.append(unit4_array)

    detailsarray.append(unit5_name_array)
    detailsarray.append(unit5_array)

    detailsarray.append(unit6_name_array)
    detailsarray.append(unit6_array)

    detailsarray.append(unit7_name_array)
    detailsarray.append(unit7_array)

    detailsarray.append(unit8_name_array)
    detailsarray.append(unit8_array)

    detailsarray.append(unit9_name_array)
    detailsarray.append(unit9_array)

    detailsarray.append(unit10_name_array)
    detailsarray.append(unit10_array)

    return detailsarray


def display_units(num_units, offset1, offset2, offset3):
    for i in range(0, num_units):
        print('<option value="' + str(i) + '">Unit ' + str(i) + '</option>')


def fetch_subject_name(subject_id, offset1, offset2, offset3):
    # detailsarray_total = fetch_subject(subject_id, 0, 0, 0, 0, 0, 0)
    # subject_name = detailsarray_total[5][0]
    # json_value = fetch_subject_query(subject_id,0,0,0,0,0,0)

    # table = dynamodb.Table('subject')
    # response = table.query(
    #
    #     KeyConditionExpression=Key('subject_id').eq(str(subject_id)) & Key('flag').eq('1')
    # )
    # json_value = response
    # decode_items = util.loads(json_value)
    # items = decode_items['Items']
    # try:
    #     subject_name = util.loads(items[0])['subject_name']
    # except:
    #     subject_name = ""
    #
    # return subject_name
    return ""


# fetch topic video cmd 2
# fetch video by video id
def fetch_video_query(cmd, video_id, subject_id, unit_num, offset3, offset4):
    table = dynamodb.Table('video')

    if cmd == 1:
        response = table.query(
            KeyConditionExpression=Key('video_id').eq(video_id)
        )
    elif cmd == 2:
        if unit_num == 0:
            # response = table.scan(
            #     FilterExpression=Attr('subject_id').eq(subject_id)
            # )
            response = table.query(
                KeyConditionExpression=Key('subject_id').eq(str(subject_id)) & Key('video_id').begins_with(str('UNIT'))
            )
        else:
            response = table.scan(
                FilterExpression=Attr('subject_id').eq(subject_id) & Attr('unit_num').eq(unit_num)
            )
    else:
        response = table.scan(
            FilterExpression=Attr('subject_id').eq(14)
        )
    return response


# fetch topic video cmd 2
# fetch video by video id
def fetch_video(cmd, video_id, subject_id, unit_num, offset3, testflag):
    detailsarray = []
    video_id_array = []
    subject_name_array = []
    video_name_array = []
    unit_num_array = []
    part_num_array = []
    video_photo_array = []
    trail_video_array = []
    full_video_array = []
    video_description_array = []
    video_priority_array = []
    video_active_array = []
    tags_array = []
    subject_id_array = []
    datentime_array = []
    view_count_array = []
    notes_array = []

    json_value = fetch_video_query(cmd, video_id, subject_id, unit_num, 0, 0)
    decode_items = util.loads(json_value)
    count = decode_items['Count']
    items = decode_items['Items']
    if testflag == 1:
        return items

    for i in range(0, count):
        video_id_array.append(util.loads(items[i])['video_id'])
        subject_name_array.append(fetch_subject_name(util.loads(items[i])['subject_id'], 0, 0, 0))  # "subject_name" +
        video_name_array.append(util.loads(items[i])['video_name'])
        unit_num_array.append(util.loads(items[i])['unit_num'])
        part_num_array.append(util.loads(items[i])['part_num'])
        video_photo_array.append(util.loads(items[i])['video_photo'])
        trail_video_array.append(util.loads(items[i])['trail_video'])
        full_video_array.append(util.loads(items[i])['full_video'])
        video_description_array.append(util.loads(items[i])['video_description'])
        video_priority_array.append(util.loads(items[i])['video_priority'])
        video_active_array.append(util.loads(items[i])['video_active'])
        tags_array.append(util.loads(items[i])['tags'])
        subject_id_array.append(util.loads(items[i])['subject_id'])
        datentime_array.append(util.loads(items[i])['datentime'])
        view_count_array.append(util.loads(items[i])['view_count'])
        try:
            notes_array.append(util.loads(items[i])['video_file'])
        except:
            notes_array.append("")

    detailsarray.append(video_id_array)
    detailsarray.append(subject_name_array)
    detailsarray.append(video_name_array)
    detailsarray.append(unit_num_array)
    detailsarray.append(part_num_array)
    detailsarray.append(video_photo_array)
    detailsarray.append(trail_video_array)
    detailsarray.append(full_video_array)
    detailsarray.append(video_description_array)
    detailsarray.append(video_priority_array)
    detailsarray.append(video_active_array)
    detailsarray.append(tags_array)
    detailsarray.append(subject_id_array)
    detailsarray.append(datentime_array)
    detailsarray.append(view_count_array)
    detailsarray.append(notes_array)

    return detailsarray


def fetch_subject_id_from_video_id(video_id, offset1, offset2, offset3):
    table = dynamodb.Table('subject')
    json_value = fetch_video_query(1, video_id, 0, 0, 0, 0)
    decode_items = util.loads(json_value)
    items = decode_items['Items']
    subject_id = util.loads(items[0])['subject_id']

    return subject_id


def fetch_video_file(video_id, offset1, offset2, offset3):
    table = dynamodb.Table('video_file')
    response = table.scan(
        FilterExpression=Attr('video_id').eq(video_id)
    )

    json_value = response
    decode_items = util.loads(json_value)
    items = decode_items['Items']
    file_name = util.loads(items[0])['file_name']
    return file_name


def fetch_user_query(cmd, user_id, offset1, offset2, offset3):
    table = dynamodb.Table('google_users')
    response = table.scan()
    return response


def fetch_user_details():
    detailsarray = []
    user_id_array = []
    user_name_array = []
    user_email_array = []
    user_phone_array = []
    user_referal_array = []
    university_id_array = []
    regulation_array = []
    branch_id_array = []

    json_response = fetch_user_query(0, 0, 0, 0, 0)
    decode_json = util.loads(json_response)
    items = decode_json['Items']
    count = decode_json['Count']

    for i in range(0, count):
        user_id_array.append(util.loads(items[i])['user_id'])
        user_name_array.append(util.loads(items[i])['user_name'])
        user_email_array.append(util.loads(items[i])['user_email'])
        user_phone_array.append(util.loads(items[i])['user_phone'])
        user_referal_array.append(util.loads(items[i])['user_referal'])
        university_id_array.append(util.loads(items[i])['university_id'])
        regulation_array.append(util.loads(items[i])['regulation'])
        branch_id_array.append(util.loads(items[i])['branch_id'])

    detailsarray.append(user_id_array)
    detailsarray.append(user_name_array)
    detailsarray.append(user_email_array)
    detailsarray.append(user_phone_array)
    detailsarray.append(user_referal_array)
    detailsarray.append(university_id_array)
    detailsarray.append(regulation_array)
    detailsarray.append(branch_id_array)

    return detailsarray

def fetch_purchased_subjects_for_user(user_id,offset1,offset2,offsaet3):
    table = dynamodb.Table('order_details')
    response = table.query(
        KeyConditionExpression=Key('user_id').eq(str(user_id)) & Key('order_id').begins_with("order"),
        FilterExpression=Attr('status_id').eq("1")
    )
    decode_items = util.loads(response)
    items = decode_items['Items']
    return items

def fetch_purchase_status(subject_id, user_id, offset1, offset2, offset3):
    # return True
    if user_id == '556' or user_id == '139' or user_id == '154' or user_id == '261':
        return True
    table = dynamodb.Table('order_details')
    response = table.query(
        KeyConditionExpression=Key('user_id').eq(str(user_id)) & Key('order_id').begins_with("order"),
        FilterExpression=Attr('subject_id').contains(str(subject_id)) & Attr('status_id').eq("1")
    )
    count = util.loads(response)['Count']
    if count >0:
        return True
    # response0 = table0.scan(
    #     FilterExpression=Attr('subject_id').eq(subject_id) & Attr('user_id').eq(user_id)
    # )
    # count0 = util.loads(response0)['Count']
    # items0 = util.loads(response0)['Items']
    # print(items0)
    # print("cccouuunttt**************")
    # print(count0)
    # if count0 == 0:
    #     return False
    # else:
    #     table = dynamodb.Table('order_details')
    #     for i in range(0, count0):
    #         order_id = util.loads(items0[i])['order_id']
    #         response = table.scan(
    #             FilterExpression=Attr('order_id').eq(order_id) & Attr('status_id').eq(1)
    #         )
    #         count = util.loads(response)['Count']
    #         if count > 0:
    #             return True

    return False


def fetch_notification(user_id, offset1, offset2, offset3):
    table = dynamodb.Table('notification')
    response = table.scan(
        FilterExpression=Attr("user_id").eq(user_id)
    )

    message_array = []

    count = util.loads(response)['Count']
    items = util.loads(response)['Items']
    for i in range(0, count):
        message_array.append(util.loads(items[i])['message'])
    detailsarray = []
    detailsarray.append(count)
    detailsarray.append(message_array)
    return detailsarray


def fetch_unit(subject_id, unit_count):
    table = dynamodb.Table('subject_unit')
    response = table.scan(
        FilterExpression=Attr("subject_id").eq(subject_id)
    )

    decode_json = util.loads(response)
    items = decode_json['Items']
    count = decode_json['Count']

    unit1_array = []
    unit2_array = []
    unit3_array = []
    unit4_array = []
    unit5_array = []
    unit6_array = []
    unit7_array = []
    unit8_array = []
    unit9_array = []
    unit10_array = []
    unit1_name_array = []
    unit2_name_array = []
    unit3_name_array = []
    unit4_name_array = []
    unit5_name_array = []
    unit6_name_array = []
    unit7_name_array = []
    unit8_name_array = []
    unit9_name_array = []
    unit10_name_array = []

    unit_heading_array = []
    unit_content_array = []
    unit_to_display = []

    if count > 0:
        unit1_array.append(util.loads(items[0])['unit1'])
        unit2_array.append(util.loads(items[0])['unit2'])
        unit3_array.append(util.loads(items[0])['unit3'])
        unit4_array.append(util.loads(items[0])['unit4'])
        unit5_array.append(util.loads(items[0])['unit5'])
        unit6_array.append(util.loads(items[0])['unit6'])
        unit7_array.append(util.loads(items[0])['unit7'])
        unit8_array.append(util.loads(items[0])['unit8'])
        unit9_array.append(util.loads(items[0])['unit9'])
        unit10_array.append(util.loads(items[0])['unit10'])
        unit1_name_array.append(util.loads(items[0])['unit1_name'])
        unit2_name_array.append(util.loads(items[0])['unit2_name'])
        unit3_name_array.append(util.loads(items[0])['unit3_name'])
        unit4_name_array.append(util.loads(items[0])['unit4_name'])
        unit5_name_array.append(util.loads(items[0])['unit5_name'])
        unit6_name_array.append(util.loads(items[0])['unit6_name'])
        unit7_name_array.append(util.loads(items[0])['unit7_name'])
        unit8_name_array.append(util.loads(items[0])['unit8_name'])
        unit9_name_array.append(util.loads(items[0])['unit9_name'])
        unit10_name_array.append(util.loads(items[0])['unit10_name'])

        if 0 < unit_count:
            unit_heading_array.append(unit1_array)
            unit_content_array.append(unit1_name_array)
            unit_to_display.append('<option value="1">Unit 1</option>')
        if 1 < unit_count:
            unit_heading_array.append(unit2_array)
            unit_content_array.append(unit2_name_array)
            unit_to_display.append('<option value="2">Unit 2</option>')
        if 2 < unit_count:
            unit_heading_array.append(unit3_array)
            unit_content_array.append(unit3_name_array)
            unit_to_display.append('<option value="3">Unit 3</option>')
        if 3 < unit_count:
            unit_heading_array.append(unit4_array)
            unit_content_array.append(unit4_name_array)
            unit_to_display.append('<option value="4">Unit 4</option>')
        if 4 < unit_count:
            unit_heading_array.append(unit5_array)
            unit_content_array.append(unit5_name_array)
            unit_to_display.append('<option value="5">Unit 5</option>')
        if 5 < unit_count:
            unit_heading_array.append(unit6_array)
            unit_content_array.append(unit6_name_array)
            unit_to_display.append('<option value="6">Unit 6</option>')
        if 6 < unit_count:
            unit_heading_array.append(unit7_array)
            unit_content_array.append(unit7_name_array)
            unit_to_display.append('<option value="7">Unit 7</option>')
        if 7 < unit_count:
            unit_heading_array.append(unit8_array)
            unit_content_array.append(unit8_name_array)
            unit_to_display.append('<option value="8">Unit 8</option>')
        if 8 < unit_count:
            unit_heading_array.append(unit9_array)
            unit_content_array.append(unit9_name_array)
            unit_to_display.append('<option value="9">Unit 9</option>')
        if 9 < unit_count:
            unit_heading_array.append(unit10_array)
            unit_content_array.append(unit10_name_array)
            unit_to_display.append('<option value="10">Unit 10</option>')

    detailsarray.append(unit_content_array)  # this is heading mistake in name
    detailsarray.append(unit_heading_array)  # this is content
    detailsarray.append(unit_to_display)

    return detailsarray


def login_popup():
    return '<div id="myLoginpage" style="display:none;" class="login-window"> <div> <a href="#" title="Close" class="modal-close" style="color:black;" onclick="closeLogin()">Close</a> <form class="form-horizontal" action="" method="post"> <div class="box box-info"> <div class="box-body"> <div class="container"> <div class="margin10"></div> <div class="col-sm-2 col-sm-offset-2" > <h2 style="padding: 16px;text-transform: capitalize;font-size: 26px;">Login With Google</h2> <a class="btn btn-block btn-social btn-google-plus" href="login.php" style=" width: 100%;border-radius: 4px; background: #ff4545;color: #fff;"> <i class="fa fa-google-plus"></i> Login </a> </div> </div> </div> </div> </form> </div> </div>'


def login_status():
    return False


def select_all(table, attr):
    var = '''<html lang="en-US" class="css3transitions"><head>'''
    return ""


def header_test():
    var = "***********************"
    var1 = """

   
    <h1> %s </h1>
"""

    var2 = "" + (var1 % (var))
    return var2


app = FlaskLambda(__name__)


# @app.route('/', methods=['GET', 'POST'])
# def test():
#     errors = []
#     results = {}
#     if request.method == "POST":
#         # get url that the user has entered
#         try:
#             url = request.form['url']
#             r = requests.get(url)
#             print(r.text)
#         except:
#             errors.append(
#                 "Unable to get URL. Please make sure it's valid and try again."
#             )
#     errors.append("ghghg")
#     errors.append("weroiuwyr")
#     return render_template('header.html', errors=errors, results=results)
def unescape(s):
    s = s.replace("&lt;", "<")
    s = s.replace("&gt;", ">")
    # this has to be last:
    s = s.replace("&amp;", "&")
    s = s.replace("&quot;", "\"")
    s = s.replace("%20", " ")
    s = s.replace("â€“", "-")
    s = s.replace("â€™", "'")
    return s


def subject_display(subject_id_array, i, subject_template):
    subject_html_to_send = ""
    subject_id_to_display = subject_id_array[0][i]
    subject_name_to_display = subject_id_array[5][i]
    subject_total_price_to_display = subject_id_array[7][i]
    subject_discounted_price_to_display = subject_id_array[8][i]
    subject_photo_to_display = subject_id_array[9][i]
    subject_desc_to_display = subject_id_array[15][i]
    video_id_to_display = subject_id_array[18][i]
    video_exist_flag = subject_id_array[16][i]

    # print("*9***********")
    # print(video_exist_flag)
    # print("*9***********")

    isExist = False
    if video_exist_flag == 2:
        isExist = True

    if subject_discounted_price_to_display == 1:
        subject_discounted_price_to_display = "Free"
    subject_data = {
        "subject_id": subject_id_to_display,
        "subject_name": subject_name_to_display,
        "subject_total_price": subject_total_price_to_display,
        "subject_discounted_price": subject_discounted_price_to_display,
        "subject_photo": subject_photo_to_display,
        "subject_desc": subject_desc_to_display,
        "video_id": video_id_to_display,
        "star_avg_rating": "5",
        "total_ratings": "150",
        "video_exists": isExist
    }
    subject_html_to_send += pystache.render(subject_template, subject_data)
    return subject_html_to_send


def syllabus_display(cmd, subject_id, num_unit):
    syllabus_html_to_send = ""

    if cmd == 1:
        session_unit_id = "0"
        return session_unit_id
    elif cmd == 2:
        session_unit_option = "All Units"
        return session_unit_option
    elif cmd == 3:
        unit_options = []
        for i in range(0, num_unit):
            unit_options.append('<option value=' + str(i + 1) + '>UNIT-' + str(i + 1) + '</option>')
        return unit_options
    else:
        syllabus_unit_array = fetch_unit(subject_id, num_unit)

        try:
            unit_heading = syllabus_unit_array[0]
            unit_content = syllabus_unit_array[1]
            syllabus_template = open("syllabus.html").read()
            for i in range(0, num_unit):
                syllabus_data = {
                    "unit_number": (i + 1),
                    "unit_heading": unit_heading[i][0],
                    "unit_content": unit_content[i][0],
                }
                syllabus_html_to_send += unescape(pystache.render(syllabus_template, syllabus_data))
        except IndexError:
            syllabus_html_to_send = ""

        return syllabus_html_to_send


def topic_video_display(cmd, video_id, subject_id, unit_id, webview_size, offset2):
    video_html_to_send = ""
    vide_view_count = 232
    topic_video_array = fetch_video(cmd, video_id, subject_id, unit_id, 0, 0)
    if webview_size == "mobile":
        video_template = open("topic_video_mobile.html").read()
    else:
        video_template = open("topic_video.html").read()
    for i in range(0, len(topic_video_array[0])):
        video_data = {
            "video_id": topic_video_array[0][i],
            "video_name": topic_video_array[2][i],
            "video_photo": topic_video_array[5][i],
            "subject_id": subject_id,
            "vide_view_count": vide_view_count,
        }
        video_html_to_send += pystache.render(video_template, video_data)

    return video_html_to_send


def subject_templete_fetch(cmd, university_id, branch_id, semester_id, university_name):
    if cmd == 1:
        subject_id_array = fetch_subject(0, 1, branch_id, semester_id, 1, university_name, 0)
    elif cmd == 2:
        subject_id_array = fetch_subject(0, 1, branch_id, semester_id, 2, university_name, 0)
    else:
        subject_id_array = fetch_subject(0, 2, 0, 0, 0, university_name, 0)
    subject_template = open("subject.html").read()
    subject_html = ""
    for i in range(0, len(subject_id_array[0])):
        subject_html += subject_display(subject_id_array, i, subject_template)

    return subject_html


def notification():
    notification_array = []
    notification_count = 0
    if user_login_status:
        notification_array = fetch_notification(str(user_id), 0, 0, 0)[1]
        notification_count = fetch_notification(str(user_id), 0, 0, 0)[0]
    header_data = {
        "notification_count": notification_count,
        "login_status": user_login_status,
        "notification_array": notification_array,
    }
    return header_data


def header_final():
    template = open('header.html').read()
    html = pystache.render(template)
    return html


def links_final():
    template = open('links.html').read()
    html = pystache.render(template)
    return html


def db_js():
    template = open('db_js_new.html').read()
    html = pystache.render(template)
    return html


def course_header_final():
    header_data = notification()
    course_header_template = open('course_header.html').read()
    course_header = pystache.render(course_header_template, header_data)
    return course_header


def course_index_final(university_id, branch_id, semester_id, university_name):
    course_subject_html_1 = subject_templete_fetch(1, university_id, branch_id, semester_id, university_name)
    course_subject_html_2 = subject_templete_fetch(2, university_id, branch_id, semester_id, university_name)
    # course_subject_html_2 = "<div>Hello World!</div>"
    heading1 = "CSE 2ND YEAR 1ST SEM"
    heading2 = "CSE 2ND YEAR 2ND SEM"
    course_index_data = {
        "login_status": user_login_status,
        "heading1": heading1,
        "heading2": heading2,
        "course_subject_html_1": course_subject_html_1,
        "course_subject_html_2": course_subject_html_2,
        "university_id": university_id,
        "branch_id": branch_id,
        "semester_id": semester_id,
        "university_name": university_name_cookie,
        "branch_name": branch_name_cookie,
        "semester_name": semester_name_cookie,
        "semester_status": semester_status,
        "branch_status": branch_status,
        "university_status": university_status,
    }
    course_index_template = open('course_index.html').read()
    course_index = unescape(pystache.render(course_index_template, course_index_data))
    return course_index


def index_final():
    # semester_suffix = "st"
    # university_name = "JNTUK"
    # index_data = {
    #     "login_status": user_login_status,
    #     "university_id": university_id,
    #     "university_array": fetch_university(0, 1, 0, 0),
    #     "branch_id": branch_id,
    #     "semester_suffix": semester_suffix,
    #     "semester_id": semester_id,
    #     "subject_html": subject_templete_fetch(0, 0, 0, 0, university_name),
    #     "university_name": university_name_cookie,
    #     "branch_name": branch_name_cookie,
    #     "semester_name": semester_name_cookie,
    #     "semester_status": semester_status,
    #     "branch_status": branch_status,
    #     "university_status": university_status,
    #
    # }
    index_template = open('index.html').read()
    # index = unescape(pystache.render(index_template, index_data))
    index = pystache.render(index_template)
    return index

def homepage_final():
    index_template = open('homepage.html').read()
    index = pystache.render(index_template)
    return index


def course_video_final(webview_size):
    if webview_size == "mobile":
        course_video_template = open('course_video_mobile.html').read()
    else:
        course_video_template = open('course_video.html').read()
    course_video = unescape(pystache.render(course_video_template))
    return course_video


def coming_soon_final(isApp):
    coming_soon_data = {
        "isApp": isApp,
    }

    coming_soon_template = open('coming_soon.html').read()
    coming_soon_html = pystache.render(coming_soon_template, coming_soon_data)
    return coming_soon_html


def google_login_final():
    google_login_template = open('google_login.html').read()
    google_login_html = pystache.render(google_login_template)
    return google_login_html


def payment_form():
    payment_form_template = open('payment_form.html').read()
    payment_form_html = pystache.render(payment_form_template)
    return payment_form_html


def payment(name, email, phone, grandtotal, order_id):
    payment = ""
    client = razorpay.Client(auth=("rzp_live_xBoLeiOILrTfRi", "HHNL5xcUj97TWnV8QRMPxjwz"))
    payment_data = {
        "amount": 1,  # int(grandtotal),
        "currency": "INR",
        "receipt": order_id,
        'payment_capture': '1',

    }

    # amount = 100
    # currency = "INR"
    # receipt = "123456"
    order_amount = 50000
    order_currency = 'INR'
    order_receipt = 'order_rcptid_11'
    notes = {'Shipping address': 'Bommanahalli, Bangalore'}  # OPTIONAL
    payment = client.order.create(data=payment_data)
    print(payment)

    payment_data_to_display = {
        "payment": payment['id'],
        "amount": int(grandtotal),
        "name": name,
        "email": email,
        "phone": phone,
        "receipt": order_id,
    }

    payment_form_template = open('payment_form.html').read()
    payment_form_html = pystache.render(payment_form_template, payment_data_to_display)
    return payment_form_html


def cookiee_test():
    value = ""
    # url = "https://n9yz799guk.execute-api.ap-south-1.amazonaws.com"
    # cookies = dict(name='jerry', password='888')
    # response = requests.get(url, cookies=cookies)
    # url = "https://n9yz799guk.execute-api.ap-south-1.amazonaws.com"
    # cookies_jar = requests.cookies.RequestsCookieJar()
    # cookies_jar.set('name', 'jerry', domain='n9yz799guk.execute-api.ap-south-1.amazonaws.com', path='/Prod/hello/c')
    # cookies_jar.set('password', 'jerry888', domain='n9yz799guk.execute-api.ap-south-1.amazonaws.com', path='/Prod/hello/c')
    # value = requests.get(url, cookies=cookies_jar)
    # print("value222*******************************")
    # print(value)
    # print("value222****************************")
    # session = requests.Session()
    # # # value = session.headers
    # print("value111*******************************")
    # print(session)
    # print("value111****************************")
    # response = session.get('https://n9yz799guk.execute-api.ap-south-1.amazonaws.com/Prod/hello/?url=cookie')
    # value = session.cookies
    # print("valueLL*******************************")
    # print(value)
    # print(response)
    # print("valueLL****************************")

    return "value"


def fetch_cookie_from_string(cookie_string):
    global name, email
    cookie_value = ""
    cookie_value_final_array = []
    cookie_value_array = cookie_string.split(';')
    cookie_value_final_array_name = []
    # print("*********************111111")
    for i in range(0, len(cookie_value_array)):
        if "email" in cookie_value_array[i]:
            cookie_value_final_array = cookie_value_array[i].split('=')
            break

    for i in range(0, len(cookie_value_array)):
        if "name" in cookie_value_array[i]:
            cookie_value_final_array_name = cookie_value_array[i].split('=')
            break
    # print("*********************2222222222")
    cookie_value = cookie_value_final_array[1]
    email = cookie_value_final_array[1]
    name = cookie_value_final_array_name[1]
    cookie_value = fetch_user_id(cookie_value)
    # print("*********************333333333333")
    return cookie_value


def common_cookies(cookie_string):
    global university_id, branch_id, semester_id, university_name_cookie, branch_name_cookie, semester_name_cookie, semester_status, branch_status, university_status
    cookie_value = ""
    cookie_value_final_array = []
    cookie_value_array = cookie_string.split(';')
    # print("*********************111111")
    cookie_value_university_array = ""
    cookie_value_branch_array = ""
    cookie_value_semester_array = ""
    university_name_cookie = ""
    branch_name_cookie = ""
    semester_name_cookie = ""
    cookie_value_subject_array = ""
    cookie_value_video_array = ""
    university_status = False
    branch_status = False
    semester_status = False

    for i in range(0, len(cookie_value_array)):
        if "university_id" in cookie_value_array[i]:
            cookie_value_university_array = cookie_value_array[i].split('=')
            university_status = True
        elif "branch_id" in cookie_value_array[i]:
            cookie_value_branch_array = cookie_value_array[i].split('=')
            branch_status = True
        elif "semester_id" in cookie_value_array[i]:
            cookie_value_semester_array = cookie_value_array[i].split('=')
            semester_status = True
        elif "university_name" in cookie_value_array[i]:
            cookie_value_university_name_array = cookie_value_array[i].split('=')

        elif "semester_name" in cookie_value_array[i]:
            cookie_value_semester_name_array = cookie_value_array[i].split('=')

        elif "branch_name" in cookie_value_array[i]:
            cookie_value_branch_name_array = cookie_value_array[i].split('=')

        # elif "subject_id" in cookie_value_array[i]:
        #     cookie_value_subject_array = cookie_value_array[i].split('=')
        #
        # elif "video_id" in cookie_value_array[i]:
        #     cookie_value_video_array = cookie_value_array[i].split('=')

    # print("*********************2222222222")
    if cookie_string != '':
        university_id = cookie_value_university_array[1]
        branch_id = cookie_value_branch_array[1]
        semester_id = cookie_value_semester_array[1]

        university_name_cookie = cookie_value_university_name_array[1]
        branch_name_cookie = cookie_value_branch_name_array[1]
        semester_name_cookie = cookie_value_semester_name_array[1]

    # cookie_subject = cookie_value_subject_array[1]
    # cookie_video = cookie_value_video_array[1]

    # print("*********************333333333333")


def fetch_user_id(email):
    # email = "pavankumarv12345678@gmail.com"
    table = dynamodb.Table('google_users')
    user_id = 0
    # print("*********************44444444444")
    response = table.scan(
        FilterExpression=Attr('email').eq(email)
    )
    # print("*********************55555555")
    decode_items = util.loads(response)
    count = decode_items['Count']

    if count == 0:
        # print("*********************666666666")
        user_id = insert_user(email)
    else:
        # print("*********************7777777777")
        items = decode_items['Items']
        user_id = util.loads(items[0])['id']

    return user_id


def insert_user(email):
    table = dynamodb.Table('google_users')
    # print("*********************888888888")
    response = table.put_item(
        Item={
            'id': 2002,
            'email': email,
        }
    )
    print("*********************9999999999")
    print(response)
    return 0


def checkout_final():
    checkout_template = open('cart.html').read()
    checkout_html = unescape(pystache.render(checkout_template))
    return checkout_html


def profile_final():
    templete = open('profile.html').read()
    profile_html = pystache.render(templete)
    return profile_html


def privacy_final():
    templete = open('privacy.html').read()
    html = pystache.render(templete)
    return html


def terms_final():
    templete = open('terms.html').read()
    html = pystache.render(templete)
    return html


def footer_final():
    templete = open('footer.html').read()
    html = pystache.render(templete)
    return html


def contact_final():
    templete = open('contact.html').read()
    html = pystache.render(templete)
    return html


def cart_final():
    templete = open('cart.html').read()
    html = pystache.render(templete)
    return html


def wishlist_final():
    templete = open('wishlist.html').read()
    html = pystache.render(templete)
    return html


def my_courses_final():
    templete = open('myCourses.html').read()
    html = pystache.render(templete)
    return html


def notification_final():
    templete = open('notification.html').read()
    html = pystache.render(templete)
    return html


def test_final():
    templete = open('../tests/test.html').read()
    html = pystache.render(templete)
    return html


def success_final():
    templete = open('success.html').read()
    html = pystache.render(templete)
    return html

def question_paper_final():
    templete = open('question_paper.html').read()
    html = pystache.render(templete)
    return html


@app.route('/post/', methods=['GET', 'POST'])
def post_return():
    # print(request.form['cmd'])
    return 'Received !'


@app.route('/', methods=['GET', 'POST'])
def lambda_handler(event, context):
    print(event)
    # print(request.form['cmd'])
    global dynamodb
    global user_login_status, university_id, university_name, university_name_cookie, branch_id, branch_name, branch_name_cookie, semester_name_cookie, semester_id, semester_status, branch_status, university_status
    global cookies
    global user_id, name, email, phone, datentime
    user_id = ""
    name = ""
    email = ""
    phone = ""
    datentime = str(datetime.datetime.now())[:-7]

    cookies = []
    dynamodb = boto3.resource('dynamodb')

    user_login_status = login_status()
    university_id = 1
    university_name = ""
    university_status = False

    branch_id = 1
    branch_name = ""  # fetch_branch_name(branch_id)
    branch_status = False

    semester_id = 1
    semester_status = False

    video_id = 200
    user_id = 0
    try:
        url = event['queryStringParameters']['url']
    except:
        url = "index"
        # url = "video_view"

    try:
        email = event['multiValueHeaders']['cookie'][0]
        # print("****************************************")
        # print(fetch_cookie_from_string(email))
        user_id = int(fetch_cookie_from_string(email))
        isUserLoggedIn = True
        user_login_status = True
    except:
        # print("###################################")
        isUserLoggedIn = False
        user_id = 0
        user_login_status = False
    try:
        print(event['multiValueHeaders']['cookie'])
        common_cookies(event['multiValueHeaders']['cookie'][0])
    except:
        common_cookies('')
    returnBody = ""
    # returnBody = event
    if url == "homepage":
        returnBody = links_final() + header_final() + homepage_final() + footer_final() + db_js()
    if url == "index":
        returnBody = links_final() + header_final()  + index_final() + footer_final()+ db_js()
    elif url == "courses":

        try:
            university_id = event['queryStringParameters']['university_id']
        except:
            university_id = 0

        try:
            branch_id = event['queryStringParameters']['branch_id']
        except:
            branch_id = 0
        try:
            semester_id = event['queryStringParameters']['semester_id']
        except:
            semester_id = 0
        try:
            university_name_cookie = event['queryStringParameters']['university_name']
        except:
            university_name_cookie = "xyz"

        try:
            branch_name_cookie = event['queryStringParameters']['branch_name']
        except:
            branch_name_cookie = "abc"
        try:
            semester_name_cookie = event['queryStringParameters']['semester_name']
        except:
            semester_name_cookie = "123"
        university_name = "JNTUK"
        returnBody = course_header_final() + course_index_final(university_id, branch_id, semester_id, university_name)
    elif url == "video_view":
        returnBody = links_final() + header_final() + course_header_final() + db_js() + course_video_final("desktop")
    elif url == "mobile_video_view":

        returnBody = course_video_final("mobile") + db_js()
    elif url == "coming_soon":
        try:
            source = event['queryStringParameters']['source']
            returnBody = coming_soon_final(True)
        except:
            returnBody = coming_soon_final(False)
    elif url == "google_login":
        returnBody = google_login_final()
    elif url == "cookie":
        returnBody = ""
    elif url == "checkout":
        returnBody = \
            () + header_final() + db_js() + checkout_final() + footer_final()
    elif url == "profile":
        returnBody = links_final() + header_final() + db_js() + profile_final() + footer_final()
    elif url == "privacy-policy":
        returnBody = links_final() + header_final() + db_js() + privacy_final() + footer_final()
    elif url == "privacy-policy_app":
        returnBody = privacy_final()
    elif url == "terms":
        returnBody = links_final() + header_final() + db_js() + terms_final() + footer_final()
    elif url == "terms_app":
        returnBody = terms_final()
    elif url == "contact":
        returnBody = links_final() + header_final() + db_js() + contact_final() + footer_final()
    elif url == "cart":
        returnBody = links_final() + header_final() + db_js() + cart_final() + footer_final()
    elif url == "wishlist":
        returnBody = links_final() + header_final() + db_js() + wishlist_final() + footer_final()
    elif url == "my_courses":
        returnBody = links_final() + header_final() + db_js() + my_courses_final() + footer_final()
    elif url == "notification":
        returnBody = links_final() + header_final() + db_js() + notification_final() + footer_final()
    elif url == "logout":
        returnBody = links_final() + header_final() + db_js() + footer_final()
    elif url == "success":
        returnBody = success_final()
    elif url == "question_paper":
        returnBody = question_paper_final()
    elif url == "test":
        # returnBody = insert_google_users("pavan", "pavan@gmail.com")
        returnBody = test_final()
    elif url == "app_api":
        # returnBody = event['body']
        try:
            data = json.loads(event['body'])
        except:
            data = event['queryStringParameters']

        cmd = int(data['cmd'])
        response11 = []
        if cmd == 11:  # db version need to attach the backend
            response11 = {
                "status": 1,
                "data": "",
                "version": 8,
                "app_version": "6.0.5"
            }
        elif cmd == 4:  # all video details for sent subject
            subject_id = data['subject_id']
            response11 = {
                "status": 1,
                "data": fetch_video(2, 0, subject_id, 0, 0, 0),
            }
        elif cmd == 8:  # subjects for start learning
            branch_id = data['branch_id']
            year_id = data['year_id']
            sub_sem_id = data['sub_sem_id']
            university_name = "JNTUK"
            response11 = {
                "status": 1,
                "data": fetch_subject(0, 1, branch_id, year_id, sub_sem_id, university_name, 0),
            }
        elif cmd == 80:  # subjects for start learning
            branch_id = data['branch_id']
            year_id = data['year_id']
            sub_sem_id = data['sub_sem_id']
            university_name = "JNTUK"
            response11 = {
                "status": 1,
                "data": fetch_subject(0, 1, branch_id, year_id, sub_sem_id, university_name, 1),
            }
        elif cmd == 1:  # subject for home page need to link university
            university_name = "JNTUK"
            response11 = {
                "status": 1,
                "data": fetch_subject(0, 2, 0, 0, 0, university_name, 0),
            }
        elif cmd == 9:
            subject_id = data['subject_id']
            user_id = data['user_id']

            response11 = {
                "status": 1,
                "data": "",
                "purchase_status": fetch_purchase_status(subject_id, user_id, 0, 0, 0),
            }
        elif cmd == 14:  # contact form
            try:
                name = data['name']
            except:
                name = ""
            email = data['email']
            phone = data['phone']
            subject = data['subject']
            comment = data['comment']

            response11 = {
                "status": insert_contact_form(name, email, phone, subject, comment),
                "data": ""
            }
        elif cmd == 10:  # insert new users
            email = data['email']
            name = data['name']
            phone = ""
            response11 = {
                "status": 1,
                "data": "",
                "user_id": insert_google_users(name, email),
                "phone": phone
            }
        elif cmd == 13:
            email = data['email']
            name = data['name']
            qualification = data['qualification']
            phone = data['phone']
            description = data['description']
            experience = data['experience']
            subjects = data['subjects']

            response11 = {
                "status": insert_professors(name, email, qualification, phone, description, experience, subjects),
                "data": "",
            }
        elif cmd == 7:
            order_id_to_update = data['order_id']
            subject_id = data['subject_id']
            task = data['task']
            user_id = data['user_id']
            phone = data['phone']
            amount = 2000

            table1 = dynamodb.Table('subject')

            response = table1.query(
                KeyConditionExpression=Key('flag').eq(str(2)) & Key('subject_id').eq(str(subject_id))
            )
            decode_json = util.loads(response)
            # count = decode_json['Count']

            items = util.loads(response)['Items']
            amount = items[0]['discounted_price']
            # amount = 1
            # count = response['Count']
            order_id = str("ORDER_") + str(uuid.uuid4())
            # subject_id_array.append(util.loads(items[i])['subject_id'])
            if task == 1:
                update_order_on_success(order_id_to_update, user_id)
                response11 = {
                    "status": 1,
                    "data": "",
                    "amount": amount,
                    "order_id": order_id_to_update,
                }
            else:
                insert_order(order_id, user_id, subject_id, amount)
                response11 = {
                    "status": 1,
                    "data": "",
                    "amount": amount,
                    "order_id": order_id,
                }















        # new cmd apis*******************
        elif cmd == 90:  # testing
            response11 = {
                "status": 1,
                "data": "",
                "version": 7,
                "app_version": "6.0.5"
            }
        elif cmd == 100:  # db version need to attach the backend
            response11 = {
                "status": 1,
                "data": "",
                "version": 14,
                "app_version": "8.0.0"
            }
        elif cmd == 101:  # insert new users / google login - need to add fcm token

            email = data['email']
            name = data['name']
            fcm_token = data['fcm_token']
            phone = ""
            response11 = {
                "status": 1,
                "data": "",
                "user_id": insert_google_users(name, email),
                "phone": phone,
                "fcm_token": str(fcm_token),
            }
        elif cmd == 110:  # update phone / google login
            print("***************************************************************************")
            print(event)
            print("***************************************************************************")
            email = data['email']
            phone = data['phone']
            response11 = {
                "status": 1,
                "data": "",
                "user_id": update_google_users(email, phone),
            }
        elif cmd == 111:  # update phone / google login
            print("***************************************************************************")
            print(event)
            print("***************************************************************************")
            email = data['email']
            phone = data['phone']
            response11 = {
                "status": 1,
                "data": "",
                "user_id": update_google_users(email, phone),
            }
        elif cmd == 102:  # subject for home page need to link university
            university_name = "JNTUK"
            response11 = {
                "status": 1,
                "data": fetch_subject(0, 2, 0, 0, 0, university_name, 1),
            }
        elif cmd == 103:  # subjects for start learning need to link university
            branch_id = data['branch_id']
            year_id = data['year_id']
            sub_sem_id = data['sub_sem_id']
            university_name = "JNTUK"
            try:
                university_id = data['university_id']
            except:
                university_id = "6"

            try:
                regulation = data['regulation']
            except:
                regulation = "R19"

            response11 = {
                "status": 1,
                "data": fetch_subject(0, 10, branch_id, year_id, sub_sem_id, university_name, 1),
                "semester_details": []
            }

        elif cmd == 104:  # purchase status for subject
            subject_id = data['subject_id']
            user_id = data['user_id']

            response11 = {
                "status": 1,
                "data": "",
                "purchase_status": fetch_purchase_status(subject_id, user_id, 0, 0, 0),
            }
        elif cmd == 105:  # all video details for sent subject

            subject_id = data['subject_id']
            response11 = {
                "status": 1,
                "data": fetch_video(2, 0, subject_id, 0, 0, 1),
            }
        elif cmd == 106:  # check out with order_id creation and to update payment status
            order_id_to_update = data['order_id']
            subject_id = data['subject_id']
            # flag = data['flag']
            try:
                university_id = data['university_id']
            except:
                university_id = ""

            task = int(data['task'])
            user_id = data['user_id']
            phone = data['phone']
            promo_code = data['promo_code']
            sub_cmd = data['sub_cmd']
            promo_value = 0
            if promo_code == "VE2021":
                promo_value = 500
            table1 = dynamodb.Table('subject_v2')
            amount = 0
            if sub_cmd == 1:
                amount = 5000
            else:
                for i in range(0, len(subject_id)):
                    response = table1.query(
                        KeyConditionExpression=Key('university_id').eq(str(university_id)) & Key('subject_id').eq(
                            str(subject_id[i]))
                    )
                    items = util.loads(response)['Items']
                    amount += int(items[0]['discounted_price'])
            # decode_json = util.loads(response)
            # count = decode_json['Count']
            if user_id == '139' or user_id == '484':
                amount = 1
            else:
                amount = amount - promo_value

            # amount = 1
            # count = response['Count']

            # subject_id_array.append(util.loads(items[i])['subject_id'])
            if task == 1:
                update_order_on_success(order_id_to_update, user_id)
                response11 = {
                    "status": 1,
                    "data": "",
                    "amount": amount,
                    "order_id": order_id_to_update,
                }
            else:
                client = razorpay.Client(auth=("rzp_live_xBoLeiOILrTfRi", "HHNL5xcUj97TWnV8QRMPxjwz"))
                payment_data = {
                    "amount": int(amount) * 100,  # int(grandtotal),
                    "currency": "INR",
                    "receipt": (str("ORD_") + str(uuid.uuid4())),
                    'payment_capture': '1',

                }
                payment = client.order.create(data=payment_data)
                # order_id = str("ORDER_") + str(uuid.uuid4())
                order_id = str(payment['id'])
                insert_order(order_id, user_id, subject_id, amount)
                response11 = {
                    "status": 1,
                    "data": "",
                    "amount": amount,
                    "order_id": order_id,
                }
        elif cmd == 107:  # professor registration
            email = data['email']
            name = data['name']
            qualification = data['qualification']
            phone = data['phone']
            description = data['description']
            experience = data['experience']
            subjects = data['subjects']

            response11 = {
                "status": insert_professors(name, email, qualification, phone, description, experience, subjects),
                "data": "",
            }
        elif cmd == 108:  # contact form
            try:
                name = data['name']
            except:
                name = ""
            email = data['email']
            phone = data['phone']
            subject = data['subject']
            comment = data['comment']

            response11 = {
                "status": insert_contact_form(name, email, phone, subject, comment),
                "data": ""
            }
        elif cmd == 109:  # Promo Code
            try:
                promo_code = data['promo_code']
            except:
                promo_code = ""
            email = data['email']

            amount = 0
            status = 0
            if promo_code == "VE2021":
                amount = 500
                status = 1
            else:
                status = 2

            response11 = {
                "status": status,
                "data": amount
            }
        elif cmd == 112:  # Promo Code

            response11 = {
                "status": 1,
                "data": "",
                "file": "unit-2_page-0018.pdf"
            }

        elif cmd == 113:  # Promo Code
            user_id = data['user_id']

            response11 = {
                "status": 1,
                "data": fetch_purchased_subjects_for_user(user_id,0,0,0),
            }

        # elif cmd == 15:
        #     order_id = data['order_id']
        #     subject_id = data['subject_id']
        #     task = data['task']
        #     user_id = data['user_id']
        #     amount = 2000
        #
        #     response11 = {
        #         "status": 1,
        #         "data": "",
        #         "amount": amount,
        #         "order_id": order_id
        #     }

        returnBody = json.dumps(util.loads(response11))
    elif url == "admin_api":

        try:
            data = json.loads(event['body'])
        except:
            data = event['queryStringParameters']

        print("***********")
        print(data)
        print("***********")

        cmd = int(data['cmd'])

        try:
            avg_rating = data['avg_rating']
        except:
            avg_rating = ""
        try:
            branch_id = data['branch_id']
        except:
            branch_id = ""
        try:
            complete_notes = data['complete_notes']
        except:
            complete_notes = ""
        try:
            date = data['date']
        except:
            date = ""
        try:
            discounted_price = data['discounted_price']
        except:
            discounted_price = ""
        try:
            flag = data['flag']
        except:
            flag = ""
        try:
            num_of_unit = data['num_of_unit']
        except:
            num_of_unit = ""
        try:
            price = data['price']
        except:
            price = ""
        try:
            priority = data['priority']
        except:
            priority = ""
        try:
            rating_count = data['rating_count']
        except:
            rating_count = ""
        try:
            regulation = data['regulation']
        except:
            regulation = ""
        try:
            semester_id = data['semester_id']
        except:
            semester_id = ""
        try:
            single_line_content = data['single_line_content']
        except:
            single_line_content = ""
        try:
            specialization = data['specialization']
        except:
            specialization = ""
        try:
            subject_description = data['subject_description']
        except:
            subject_description = ""
        try:
            subject_name = data['subject_name']
        except:
            subject_name = ""
        try:
            subject_photo = data['subject_photo']
        except:
            subject_photo = ""
        try:
            subject_points = data['subject_points']
        except:
            subject_points = ""
        try:
            subject_time = data['subject_time']
        except:
            subject_time = ""
        try:
            tags = data['tags']
        except:
            tags = ""
        try:
            unit1 = data['unit1']
        except:
            unit1 = ""
        try:
            unit10 = data['unit10']
        except:
            unit10 = ""
        try:
            unit10_name = data['unit10_name']
        except:
            unit10_name = ""
        try:
            unit1_name = data['unit1_name']
        except:
            unit1_name = ""
        try:
            unit2 = data['unit2']
        except:
            unit2 = ""
        try:
            unit2_name = data['unit2_name']
        except:
            unit2_name = ""
        try:
            unit3 = data['unit3']
        except:
            unit3 = ""
        try:
            unit3_name = data['unit3_name']
        except:
            unit3_name = ""
        try:
            unit4 = data['unit4']
        except:
            unit4 = ""
        try:
            unit4_name = data['unit4_name']
        except:
            unit4_name = ""
        try:
            unit5 = data['unit5']
        except:
            unit5 = ""
        try:
            unit5_name = data['unit5_name']
        except:
            unit5_name = ""
        try:
            unit6 = data['unit6']
        except:
            unit6 = ""
        try:
            unit6_name = data['unit6_name']
        except:
            unit6_name = ""
        try:
            unit7 = data['unit7']
        except:
            unit7 = ""
        try:
            unit7_name = data['unit7_name']
        except:
            unit7_name = ""
        try:
            unit8 = data['unit8']
        except:
            unit8 = ""
        try:
            unit8_name = data['unit8_name']
        except:
            unit8_name = ""
        try:
            unit9 = data['unit9']
        except:
            unit9 = ""
        try:
            unit9_name = data['unit9_name']
        except:
            unit9_name = ""
        try:
            university_id = data['university_id']
        except:
            university_id = ""
        try:
            university_name = data['university_name']
        except:
            university_name = ""
        try:
            subject_id = data['subject_id']
        except:
            subject_id = ""

        response11 = []

        if cmd == 100:  # db version need to attach the backend
            insert_subject_from_admin(avg_rating, branch_id, complete_notes, date, discounted_price, flag,
                                      num_of_unit, price, priority, rating_count, regulation,
                                      semester_id, single_line_content, specialization, subject_description, subject_id,
                                      subject_name, subject_photo, subject_points, subject_time, tags, unit1, unit10,
                                      unit10_name, unit1_name, unit2, unit2_name, unit3, unit3_name, unit4, unit4_name,
                                      unit5, unit5_name, unit6, unit6_name, unit7, unit7_name, unit8, unit8_name, unit9,
                                      unit9_name, university_id)
            response11 = {
                "status": 1,
                "data": ""
            }
        elif cmd == 1002:  # db version need to attach the backend

            try:
                subject_id = data['subject_id']
            except:
                subject_id = ""
            try:
                video_id = data['video_id']
            except:
                video_id = ""
            try:
                video_name = data['video_name']
            except:
                video_name = ""
            try:
                unit_num = data['unit_num']
            except:
                unit_num = ""
            try:
                part_num = data['part_num']
            except:
                part_num = ""
            try:
                video_photo = data['video_photo']
            except:
                video_photo = ""
            try:
                video_file = data['video_file']
            except:
                video_file = ""
            try:
                trail_video = data['trail_video']
            except:
                trail_video = ""
            try:
                full_video = data['full_video']
            except:
                full_video = ""
            try:
                video_description = data['video_description']
            except:
                video_description = ""
            try:
                video_priority = data['video_priority']
            except:
                video_priority = ""
            try:
                video_active = data['video_active']
            except:
                video_active = ""
            try:
                tags = data['tags']
            except:
                tags = ""
            try:
                video_file = data['video_file']
            except:
                video_file = ""

            insert_video_from_admin(subject_id,video_id, video_name, unit_num, part_num, trail_video, full_video, video_file,
                                      video_description, video_priority, video_active, tags, video_photo)
            response11 = {
                "status": 1,
                "data": ""
            }
        elif cmd == 103:
            try:
                date = data['date']
            except:
                date = ""

            try:
                semester_discounted_price = data['semester_discounted_price']
            except:
                semester_discounted_price = ""

            try:
                flag = data['flag']
            except:
                flag = ""

            try:
                semester_photo = data['semester_photo']
            except:
                semester_photo = ""

            try:
                semester_price = data['semester_price']
            except:
                semester_price = ""

            try:
                regulation = data['regulation']
            except:
                regulation = ""

            try:
                semester_description = data['semester_description']
            except:
                semester_description = ""

            try:
                subject_id = data['subject_id']
            except:
                subject_id = ""

            try:
                university_id = data['university_id']
            except:
                university_id = ""

            insert_semester_from_admin(date, semester_discounted_price, flag, semester_photo, semester_price,
                                       regulation,
                                       semester_description, subject_id, university_id)
            response11 = {
                "status": 1,
                "data": ""
            }
        elif cmd == 106:
            response11 = {
                "status": 1,
                "data": fetch_subject_query("", 106, "", "", university_name, university_id, 0)
            }

        returnBody = json.dumps(util.loads(response11))
    # returnBody += str(email)
    # returnBody = payment_form()+payment()
    # returnBody = coming_soon_final(True)
    # content = header + index + footer()
    # content = course_header_final() + course_video_final(video_id)
    # content = "course_header_final() + str(syllabus_display(0, video_details_array[12][0], subject_details_array[17][0]))"
    # returnBody = ""
    return {
        "statusCode": 200,
        "body": returnBody,
        "headers": {
            'Content-Type': 'text/html',
            'Content-Type': 'text/json", "application/json',
        },
        "multiValueHeaders": {
            "X-Test-Header": ["baking experiment"],
            "Set-Cookie": cookies,
            "Content-Type": ["text/html", "text/plain"]
        }
    }


def update_order_on_success(order_id, user_id):
    table = dynamodb.Table('order_details')
    response = table.update_item(
        Key={
            'user_id': user_id,
            'order_id': order_id,
        },
        UpdateExpression="set status_id=:status_id",
        ExpressionAttributeValues={
            ":status_id": "1"
        },
        ReturnValues="UPDATED_NEW"
    )

    print(response)


def insert_semester_from_admin(date, semester_discounted_price, flag, semester_photo, semester_price, regulation,
                               semester_description, subject_id, university_id):
    table = dynamodb.Table('subject_v2')
    response = table.put_item(
        Item={

            'date': date,
            'semester_discounted_price': semester_discounted_price,
            'flag': flag,
            'semester_photo': semester_photo,
            'semester_price': semester_price,
            'regulation': regulation,
            'semester_description': semester_description,
            'subject_id': subject_id,
            'university_id': university_id
        }
    )


def insert_subject_from_admin(avg_rating, branch_id, complete_notes, date, discounted_price, flag,
                              num_of_unit, price, priority, rating_count, regulation, semester_id, single_line_content,
                              specialization, subject_description, subject_id, subject_name, subject_photo,
                              subject_points, subject_time, tags, unit1, unit10, unit10_name, unit1_name, unit2,
                              unit2_name, unit3, unit3_name, unit4, unit4_name, unit5, unit5_name, unit6, unit6_name,
                              unit7, unit7_name, unit8, unit8_name, unit9, unit9_name, university_id):
    table = dynamodb.Table('subject_v2')
    response = table.put_item(
        Item={
            'avg_rating': avg_rating,
            'branch_id': branch_id,
            'complete_notes': complete_notes,
            'date': date,
            'discounted_price': discounted_price,
            'flag': flag,
            'num_of_unit': num_of_unit,
            'price': price,
            'priority': priority,
            'rating_count': rating_count,
            'regulation': regulation,
            'semester_id': semester_id,
            'single_line_content': single_line_content,
            'specialization': specialization,
            'subject_description': subject_description,
            'subject_id': subject_id,
            'subject_name': subject_name,
            'subject_photo': subject_photo,
            'subject_points': subject_points,
            'subject_time': subject_time,
            'tags': tags,
            'unit1': unit1,
            'unit10': unit10,
            'unit10_name': unit10_name,
            'unit1_name': unit1_name,
            'unit2': unit2,
            'unit2_name': unit2_name,
            'unit3': unit3,
            'unit3_name': unit3_name,
            'unit4': unit4,
            'unit4_name': unit4_name,
            'unit5': unit5,
            'unit5_name': unit5_name,
            'unit6': unit6,
            'unit6_name': unit6_name,
            'unit7': unit7,
            'unit7_name': unit7_name,
            'unit8': unit8,
            'unit8_name': unit8_name,
            'unit9': unit9,
            'unit9_name': unit9_name,
            'university_id': university_id,
        }
    )

def insert_video_from_admin(subject_id, video_id, video_name, unit_num, part_num, trail_video, full_video, video_file,
                                      video_description, video_priority, video_active, tags, video_photo):
    table = dynamodb.Table('video')
    response = table.put_item(
        Item={
            'subject_id': subject_id,
            'video_id': video_id,
            'video_name': video_name,
            'unit_num': unit_num,
            'part_num': part_num,
            'trail_video': trail_video,
            'full_video': full_video,
            'video_file': video_file,
            'video_description': video_description,
            'video_priority': video_priority,
            'video_active': video_active,
            'tags': tags,
            'video_photo': video_photo,

        }
    )


def insert_order(order_id, user_id, subject_id, amount):
    table = dynamodb.Table('order_details')
    response = table.put_item(
        Item={
            "order_id": str(order_id),
            "user_id": user_id,
            "subject_id": subject_id,
            "datentime": datentime,
            "order_total_price": str(amount),
            "payed_price": str(amount),
            "promo_code": "",
            "promo_value": "0",
            "status_id": "0",
            "vecoins_used": "0",
            "wallet_id": ""
        }
    )


def insert_contact_form(name, email, phone, subject, comment):
    # write filters
    if name == "" or email == "":
        return 2
    table = dynamodb.Table('contact_form')
    response = table.put_item(
        Item={
            "name": name,
            "email": email,
            "phone": phone,
            "subject": subject,
            "comment": comment,
            "datentime": datentime
        }
    )
    return 1


def insert_professors(name, email, qualification, phone, description, experience, subjects):
    table = dynamodb.Table('professors')

    uuid1 = uuid.uuid4()

    response = table.query(
        KeyConditionExpression=Key('email').eq(str(email))
    )

    decode_json = util.loads(response)
    count = decode_json['Count']
    if count > 0:
        return 2
    else:
        response = table.put_item(
            Item={
                "id": str(uuid1),
                "name": name,
                "email": email,
                "qualification": qualification,
                "phone": phone,
                "description": description,
                "experience": experience,
                "subjects": subjects,
                "datentime": datentime,
            }
        )

    return 1


def insert_google_users(name, email):
    global phone
    table = dynamodb.Table('google_users')
    uuid1 = uuid.uuid4()

    response = table.query(
        KeyConditionExpression=Key('email').eq(str(email))
    )

    decode_json = util.loads(response)
    count = decode_json['Count']
    if count > 0:
        items = decode_json['Items']
        uuid1 = util.loads(items)[0]['id']
        try:
            phone = util.loads(items)[0]['phone']
        except:
            phone = ""
        # uuid1 = decode_json
    else:
        response = table.put_item(
            Item={
                "id": str(uuid1),
                "name": name,
                "email": email,
                "datentime": datentime,
            }
        )

    return str(uuid1)


def update_google_users(email, phone):
    table = dynamodb.Table('google_users')

    response = table.update_item(
        Key={
            'email': email
        },
        UpdateExpression="set phone=:phone",
        ExpressionAttributeValues={
            ":phone": str(phone)
        },
        ReturnValues="UPDATED_NEW"
    )


def create_table():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.create_table(
        TableName='users',

        KeySchema=[
            {
                'AttributeName': 'username',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'last_name',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'username',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'last_name',
                'AttributeType': 'S'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

    table.meta.client.get_waiter('table_exists').wait(TableName='users')

    # dynamodb = boto3.resource('dynamodb')
    # table = dynamodb.create_table(
    #     TableName='users',
    #     KeySchema=[
    #         {
    #             'AttribiteName': 'username',
    #             'KeyType': 'HASH'
    #         },
    #         {
    #             'AttribiteName': 'lastname',
    #             'KeyType': 'RANGE'
    #         }
    #     ],
    #     AttributeDefinitions=[
    #         {
    #             'AttributeName': 'username',
    #             'AttributeType': 'S'
    #         },
    #         {
    #             'AttributeName': 'last_name',
    #             'AttributeType': 'S'
    #         },
    #     ],
    #     ProvisionedThroughput={
    #         'ReadCapacityUnits': 5,
    #         'WriteCapacityUnits': 5
    #     }
    # )
    #
    # table.meta.client.getwaiter('table_exists').wait(TableName='users')
    # print(table.item_count)

    # try:
    #     ip = requests.get("http://checkip.amazonaws.com/")
    # except requests.RequestException as e:
    #     # Send some context about this error to Lambda Logs
    #     print(e)

    #     raise e+

    # dynamodb = boto3.resource('dynamodb')
    # table = dynamodb.Table('users')
    # print(table.creation_date_time)
    #
    # table.put_item(
    #     Item={
    #         'username':'pavan',
    #         'last_name': 'kumar',
    #         'extra': 'testing',
    #     }
    # )

    # url = event['params']['querystring']['url']
    # url = context["url"]
    # content = url
    # content = '<!DOCTYPE html><html lang="en-US" class="css3transitions"><head><script async src="https://www.googletagmanager.com/gtag/js?id=AW-476148313"></script><script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)};gtag("js",new Date());gtag("config","AW-476148313");</script><script>!function(t,r,u,f,e,n,a){if(t.fbq)return;e=t.fbq=function(){e.callMethod?e.callMethod.apply(e,arguments):e.queue.push(arguments)};if(!t._fbq)t._fbq=e;e.push=e;e.loaded=!0;e.version="2.0";e.queue=[];n=r.createElement(u);n.async=!0;n.src=f;a=r.getElementsByTagName(u)[0];a.parentNode.insertBefore(n,a)}(window,document,"script","");fbq("init","206402467639054");fbq("track","PageView");</script><style>.login-window{position:fixed;background-color:rgb(33 33 33 / 81%);top:0;right:0;bottom:0;left:0;z-index:999;-webkit-transition:all 0.3s;transition:all 0.3s}.login-window:target{visibility:visible;opacity:1;pointer-events:auto}.login-window > div{width:400px;position:absolute;top:50%;left:50%;-webkit-transform:translate(-50%, -50%);transform:translate(-50%, -50%);padding:2em;background:#ffffff}.login-window header{font-weight:bold}.login-window h1{font-size:150%;margin:0 0 15px}.modal-close{color:#aaa;line-height:50px;font-size:80%;position:absolute;right:0;text-align:center;top:0;width:70px;text-decoration:none}.modal-close:hover{color:black}.login-window div:not(:last-of-type){margin-bottom:15px}small{color:#aaa}.btn{background-color:#fff;padding:1em 1.5em;border-radius:3px;text-decoration:none}.btn i{padding-right:0.3em}</style><meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1"><link rel="pingback" href="" /><title>VEteach online video lessons platform</title><meta name="keywords" content="Previous Question papers, online Btech courses for all Branches, Live Classes for Btech Students, Best online classes for Btech students, Btech Online Classes, Live classes for Btech. "><meta name="description" content="Veteach is a leading online learning platform for Btech Engineering Students learn from top faculty in India with practical learning and Previous Question papers of CSE, IT, ECE, EEE, MECH, CIVIL in the most interesting way."><link rel=“canonical” href=“https://veteach.in” /><script async src="https://www.googletagmanager.com/gtag/js?id=G-LNKK9J07HL"></script><script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)};gtag("js",new Date());gtag("config","G-LNKK9J07HL");</script><link rel="stylesheet" id="redux-google-fonts-zeroone_redata-css" href="https://fonts.googleapis.com/css?family=Karla%3A700%7COpen+Sans%7CRaleway%7CMontserrat%3A300%2C400%2C500%2C600%2C700%2C800%2C900%7CLato%3A300%7Clato%7CHind%3A300%2C400%2C500%2C600%2C700&subset=latin&ver=4.9.15" type="text/css" media="all" /><link rel="icon" type="image/png" href="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/assets/uploads/favicon.jpg"><link rel="stylesheet" id="rs-plugin-settings-css" href="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/css/settings03e2.css" type="text/css" media="all" /><link rel="stylesheet" as="font" href="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/css/font.css" type="text/css" /><link rel="stylesheet" id="style-css" href="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/assets/maincss/1styleca80.css?v=2" type="text/css" media="all" /><link rel="stylesheet" id="style-css" href="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/assets/maincss/styleca80.css?v=2" type="text/css" media="all" /><link rel="stylesheet" id="zeroone-bootstrap-responsive-css" href="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/css/bootstrap-responsiveca80.css" type="text/css" media="all" /><link rel="stylesheet" id="jquery.fancybox-css" href="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/css/jquery.fancybox950b.css" type="text/css" media="all" /><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"><link rel="stylesheet" id="idangerous.swiper-css" href="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/css/idangerous.swiperca80.css" type="text/css" media="all" /><link rel="stylesheet" id="owl.carousel-css" href="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/css/owl.carouselca80.css" type="text/css" media="all" /><link rel="stylesheet" id="owl.theme-css" href="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/css/owl.themeca80.css" type="text/css" media="all" /><link rel="stylesheet" id="zeroone-dynamic-css-css" href="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/css/admin-ajax1b5d.css" type="text/css" media="all" /><link rel="stylesheet" id="js_composer_front-css" href="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/css/js_composer.min7661.css" type="text/css" media="all" /><link rel="stylesheet" type="text/css" href="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/css/style.css?v=25"><link rel="stylesheet" type="text/css" href="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/css/mobilemode.css?v=6"><script type="text/javascript" src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/js/jqueryb8ff.js"></script><script type="text/javascript" src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/js/jquery-migrate.min330a.js"></script><script type="text/javascript" src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/js/jquery.themepunch.tools.min03e2.js"></script><script type="text/javascript" src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/js/jquery.themepunch.revolution.min03e2.js"></script><script type="text/javascript" src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/js/revolution.extension.slideanims.min.js"></script><script type="text/javascript" src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/js/revolution.extension.layeranimation.min.js"></script><script type="text/javascript" src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/js/revolution.extension.parallax.min.js"></script><script type="text/javascript" src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/js/pathformer68b3.js"></script><script type="text/javascript" src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/js/vivus68b3.js"></script><script type="text/javascript" src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/js/slide1.js"></script><script type="text/javascript" src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/js/slide2.js"></script><script type="text/javascript" src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/js/slide3.js"></script></head><style type="text/css">@media (min-width: 768px){.col-sm-offset-2{margin-left:0 !important}}img#wpstats{display:none}</style><style type="text/css">.recentcomments a{display:inline !important;padding:0 !important;margin:0 !important}</style><meta name="generator" content=""/><meta name="generator" content="" /><script type="text/javascript">function setREVStartSize(e){try{var f=jQuery(window).width(),h=9999,l=0,u=0,n=0,i=0,c=0,r=0;if(e.responsiveLevels&&(jQuery.each(e.responsiveLevels,function(i,e){e>f&&(h=l=e,n=i),f>e&&e>l&&(l=e,u=i)}),h>l&&(n=u)),i=e.gridheight[n]||e.gridheight[0]||e.gridheight,c=e.gridwidth[n]||e.gridwidth[0]||e.gridwidth,r=f/c,r=r>1?1:r,i=Math.round(r*i),"fullscreen"==e.sliderLayout){var t=(e.c.width(),jQuery(window).height());if(void 0!=e.fullScreenOffsetContainer){var s=e.fullScreenOffsetContainer.split(",");if(s)jQuery.each(s,function(i,e){t=jQuery(e).length>0?t-jQuery(e).outerHeight(!0):t}),e.fullScreenOffset.split("%").length>1&&void 0!=e.fullScreenOffset&&e.fullScreenOffset.length>0?t-=jQuery(window).height()*parseInt(e.fullScreenOffset,0)/100:void 0!=e.fullScreenOffset&&e.fullScreenOffset.length>0&&(t-=parseInt(e.fullScreenOffset,0))};i=t}else void 0!=e.minHeight&&i<e.minHeight&&(i=e.minHeight);e.c.closest(".rev_slider_wrapper").css({height:i})}catch(d){console.log("Failure at Presize of Slider:"+d)}};</script></noscript><script src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/js/modernizr.custom.js"></script><style>.cbp-spmenu{background:#47a3da;position:fixed}.cbp-spmenu h3{color:#afdefa;font-size:1.9em;padding:20px;margin:0;font-weight:300;background:#0d77b6}.cbp-spmenu a{display:block;color:#fff;font-size:1.1em;font-weight:300}.cbp-spmenu a:hover{background:#258ecd}.cbp-spmenu a:active{background:#afdefa;color:#47a3da}.cbp-spmenu-vertical{width:240px;height:100%;top:0;z-index:1000}.cbp-spmenu-vertical a{border-bottom:1px solid #258ecd;padding:1em}.cbp-spmenu-horizontal{width:100%;height:150px;left:0;z-index:1000;overflow:hidden}.cbp-spmenu-horizontal h3{height:100%;width:20%;float:left}.cbp-spmenu-horizontal a{float:left;width:20%;padding:0.8em;border-left:1px solid #258ecd}.cbp-spmenu-left{left:-240px}.cbp-spmenu-right{right:-240px}.cbp-spmenu-left.cbp-spmenu-open{left:0px}.cbp-spmenu-right.cbp-spmenu-open{right:0px}.cbp-spmenu-top{top:-150px}.cbp-spmenu-bottom{bottom:-150px}.cbp-spmenu-top.cbp-spmenu-open{top:0px}.cbp-spmenu-bottom.cbp-spmenu-open{bottom:0px}.cbp-spmenu-push{overflow-x:hidden;position:relative;left:0}.cbp-spmenu-push-toright{left:240px}.cbp-spmenu-push-toleft{left:-240px}.cbp-spmenu,.cbp-spmenu-push{-webkit-transition:all 0.3s ease;-moz-transition:all 0.3s ease;transition:all 0.3s ease}@media screen and (max-width: 55.1875em){.cbp-spmenu-horizontal{font-size:75%;height:110px}.cbp-spmenu-top{top:-110px}.cbp-spmenu-bottom{bottom:-110px}}@media screen and (max-height: 26.375em){.cbp-spmenu-vertical{font-size:90%;width:190px}.cbp-spmenu-left,.cbp-spmenu-push-toleft{left:-190px}.cbp-spmenu-right{right:-190px}.cbp-spmenu-push-toright{left:190px}}.card2{max-width:300px;margin:auto;text-align:center;font-family:arial}.title2{color:grey;font-size:18px}button2{border:none;outline:0;display:inline-block;padding:8px;color:white;background-color:#000;text-align:center;cursor:pointer;width:100%;font-size:18px}button2:hover,a:hover{opacity:0.7}</style><style>@import "https://fonts.googleapis.com/css?family=Montserrat";body{position:relative;width:100%;height:100vh;font-family:Montserrat}.wrap{position:absolute;top:50%;left:50%;-webkit-transform:translate(-50%, -50%);transform:translate(-50%, -50%)}.text{color:#fbae17;display:inline-block;margin-left:5px}.bounceball{position:relative;display:inline-block;height:37px;width:15px}.bounceball:before{position:absolute;content:"";display:block;top:0;width:15px;height:15px;border-radius:50%;background-color:#fbae17;-webkit-transform-origin:50%;transform-origin:50%;-webkit-animation:bounce 500ms alternate infinite ease;animation:bounce 500ms alternate infinite ease}@-webkit-keyframes bounce{0%{top:30px;height:5px;border-radius:60px 60px 20px 20px;-webkit-transform:scaleX(2);transform:scaleX(2);}35%{height:15px;border-radius:50%;-webkit-transform:scaleX(1);transform:scaleX(1);}100%{top:0;}}@keyframes bounce{0%{top:30px;height:5px;border-radius:60px 60px 20px 20px;-webkit-transform:scaleX(2);transform:scaleX(2);}35%{height:15px;border-radius:50%;-webkit-transform:scaleX(1);transform:scaleX(1);}100%{top:0;}}::-webkit-scrollbar{width:10px;transition:width 2s linear}::-webkit-scrollbar-track{box-shadow:inset 0 0 5px grey;border-radius:10px;transition:width 2s linear}::-webkit-scrollbar-thumb{background:#00b0f0;border-radius:10px;opacity:0.8;transition:width 2s linear}</style><body class="home page-template-default page page-id-4 header_1 fullwidth_slider_page header_transparency wpb-js-composer js-comp-ver-5.4.2 vc_responsive" style="margin:0"><div id="myLoginpage" style="display:none" class="login-window"><div><a href="#" title="Close" class="modal-close" style="color:black" onclick="closeLogin()">Close</a><form class="form-horizontal" action="" method="post"><div class="box box-info"><div class="box-body"><div class="container"><div class="margin10"></div><div class="col-sm-2 col-sm-offset-2"><h2 style="padding:16px;text-transform:capitalize;font-size:26px">Login With Google</h2><a class="btn btn-block btn-social btn-google-plus" href="login.php" style="width:100%;border-radius:4px;background:#ff4545;color:#fff"><i class="fa fa-google-plus"></i> Login </a></div></div></div></div></form></div></div><div class="viewport " id="Safe"><div class="header_wrapper header_1 normal background--light "><header id="header" class="" style="z-index:99999999"><div class="container-fluid"><div class="row-fluid"><div class="span12"><div id="logo" class=""><a href="index.php"><img class="logomak" src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/assets/uploads/logo.png" alt="" /></a></div><div class="cbp-spmenu-push"><nav class="cbp-spmenu cbp-spmenu-vertical cbp-spmenu-right" id="cbp-spmenu-s2"><a href="javascript:void(0)" class="" onClick="closeNav()">X Close</a><div class="container"><div class="margin10"></div><div class="col-sm-2 col-sm-offset-2"><a class="btn btn-block btn-social btn-google-plus" href="login.php" style="width:100%;border-radius:4px;background:#ff4545;color:#fff;margin-top:108px"><i class="fa fa-google-plus"></i> Login </a></div></div><br><br><style>.btn-bt.rounded1{color:#ffffff;background:#f2f2f2;border-color:#f2f2f2}</style><style>.dropbtn{color:#00b0f0;padding:4px;font-size:21px;border:none;cursor:pointer}.dropdown{position:relative;display:inline-block}.dropdown-content{display:none;position:absolute;background-color:#f1f1f1;min-width:160px;overflow:auto;box-shadow:0px 8px 16px 0px rgba(0,0,0,0.2);z-index:1}.dropdown-content a{color:black;font-size:13px;text-decoration:none;display:block}.dropdown a:hover{background-color:#ddd}.show{display:block}#notificationContainer{background-color:#fff;overflow:visible;position:fixed;border-radius:15px;top:55px;min-height:322px;box-shadow:0 25px 50px -12px rgba(0,0,0,.25);right:52px;width:400px;z-index:-1}#notificationContainer:before{content:"";display:block;position:absolute;width:0;height:0;color:transparent;border:10px solid black;border-color:transparent transparent white;margin-top:-20px;right:52px}#notificationTitle{font-weight:bold;padding:8px;font-size:13px;background-color:#ffffff;position:absolute;z-index:1000;width:384px;border-bottom:1px solid #dddddd}#notificationsBody{padding:33px 0px 0px 0px !important}#notificationFooter{text-align:center;font-weight:bold;padding:7px;font-size:12px;border-top:1px solid #dddddd}#notification_count{padding:3px 7px 3px 7px;background:#cc0000;color:#ffffff;font-weight:bold;margin-left:7px;border-radius:9px;-moz-border-radius:9px;-webkit-border-radius:9px;position:absolute;margin-top:-11px;font-size:11px}.notifications ul{list-style-type:none;display:inline-block;padding-left:12px}.notifications ul li{display:block;padding:4px;margin:4px;font-weight:bold}.badge{position:absolute;top:-4px;right:0px;padding:1px 6px;border-radius:50%;background-color:red;color:white}</style></nav></div><button class="openbtn btn-bt rounded rounded1 header_button btnad" onclick="myloginFunction()"><img src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/images/loginlogo.png" style="width:40px"></button></div></div></div></header><style>.portfolio-item.chrome span a:hover{background:#fff !important;color:#0e0e0e !important;border-color:#fff !important}</style><style type="text/css">.rtxt{padding-top:161px;font:normal 44px/50px Arial, sans-serif;color:rgb(60, 72, 82)}b{float:left;overflow:hidden;position:relative;height:50px}.textrot{display:inline-block;color:rgb(60, 72, 82);position:relative;white-space:nowrap;top:0;left:0;animation:move 10s;animation-iteration-count:infinite;animation-delay:3s}@keyframes move{0%{top:0px;}15%{top:0px;}20%{top:-50px;}35%{top:-50px;}40%{top:-100px;}55%{top:-100px;}60%{top:-150px;}75%{top:-150px;}80%{top:-200px;}}.hover_bkgr_fricc{background:rgba(0,0,0,.4);cursor:pointer;display:none;height:100%;position:fixed;text-align:center;top:0;width:100%;z-index:10000}.hover_bkgr_fricc .helper{display:inline-block;height:100%;vertical-align:middle}.hover_bkgr_fricc > div{background-color:#fff;box-shadow:10px 10px 60px #555;display:inline-block;height:auto;max-width:551px;min-height:100px;vertical-align:middle;width:60%;position:relative;border-radius:8px;padding:15px 5%}#at_hover a{font-size:10px !important;font-weight:100 !important}.popupCloseButton{background-color:#fff;border:3px solid #999;border-radius:50px;cursor:pointer;display:inline-block;font-family:arial;font-weight:bold;position:absolute;top:-20px;right:-20px;font-size:25px;line-height:30px;width:30px;height:30px;text-align:center}.popupCloseButton:hover{background-color:#ccc}.trigger_popup_fricc{cursor:pointer;font-size:20px;margin:20px;display:inline-block;font-weight:bold}</style><style>.modal-window{position:fixed;background-color:rgb(33 33 33 / 81%);top:0;right:0;bottom:0;left:0;z-index:999;-webkit-transition:all 0.3s;transition:all 0.3s}.modal-window:target{visibility:visible;opacity:1;pointer-events:auto}.modal-window > div{width:400px;position:absolute;top:50%;left:50%;-webkit-transform:translate(-50%, -50%);transform:translate(-50%, -50%);padding:2em;background:#ffffff}.modal-window header{font-weight:bold}.modal-window h1{font-size:150%;margin:0 0 15px}.modal-close{color:#aaa;line-height:50px;font-size:80%;position:absolute;right:0;text-align:center;top:0;width:70px;text-decoration:none}.modal-close:hover{color:black}.modal-window div:not(:last-of-type){margin-bottom:15px}small{color:#aaa}.btn{background-color:#fff;padding:1em 1.5em;border-radius:3px;text-decoration:none}.btn i{padding-right:0.3em}</style><div id="myUniversitypage" class="modal-window" style="display:none"><div><a href="#" title="Close" class="modal-close" style="color:black" onclick="closeUniversity()">Close</a><form class="form-horizontal" action="" method="post"><div class="box box-info"><div class="box-body"><div class="form-group"><label for="" class="col-sm-3 control-label">Select University <span>*</span></label><div class="col-sm-12"><select name="university_id" class="form-control select2" id="first" required><option value="">Select University</option><option value="4">JNTUH</option><option value="5">JNTUA</option><option value="6">JNTUK</option></select></div><div class="col-sm-12"><select name="branch_id" class="form-control select2" id="branch_popup_select" required><option value="">Select Branch</option><option value="1">ECE</option><option value="2">CSE</option><option value="3">EEE</option><option value="4">CIVIL</option><option value="5">MECH</option></select></div><div class="col-sm-12"><select name="semester_id" class="form-control select2" id="first" required><option value="">Select Year</option><option value="1">1st Year</option><option value="2">2nd Year</option><option value="3">3rd Year</option><option value="4">4th Year</option></select></div></div><div class="form-group"><label for="" class="col-sm-3 control-label"></label><div class="col-sm-12"><button type="submit" class="openbtn btn-bt rounded " name="user_university" style="width:100%;height:49px">Submit</button></div></div></div></div></form></div></div><link rel="stylesheet" href="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/css/fstdropdown.css"><div class="top_wrapper"><section id="slider-fullwidth" class="slider "><div id="rev_slider_2_1_wrapper" class="rev_slider_wrapper fullscreen-container" data-source="gallery" style="background:transparent;padding:0px"><div id="rev_slider_2_1" class="rev_slider fullscreenbanner hello" style="display:none" data-version="5.4.6"><ul><li class="backgroundst" data-index="rs-2" data-transition="fade" data-slotamount="default" data-hideafterloop="0" data-hideslideonmobile="off" data-easein="default" data-easeout="default" data-masterspeed="300" data-rotate="0" data-saveperformance="off" data-title="Slide" data-param1="" data-param2="" data-param3="" data-param4="" data-param5="" data-param6="" data-param7="" data-param8="" data-param9="" data-param10="" data-description="" style="background-color:#f2f2f2;background-size:100%;background-repeat:no-repeat;background-image: url(https://veteachwebfiles.s3.ap-south-1.amazonaws.com/images/final.png);"><div class="tp-caption mobileman1 tp-resizeme" id="slide-2-layer-6" data-x="1" data-y="700" data-width="["562"]" data-height="["auto"]" data-type="text" data-responsive_offset="on" data-frames="[{"delay":2000,"speed":600,"frame":"0","from":"y:[100%];z:0;rX:0deg;rY:0;rZ:0;sX:1;sY:1;skX:0;skY:0;opacity:0;","to":"o:1;","ease":"Power4.easeInOut"},{"delay":"wait","speed":200,"frame":"999","to":"opacity:0;","ease":"Power3.easeInOut"}]" data-textAlign="["inherit","inherit","inherit","inherit"]" data-paddingtop="[0,0,0,0]" data-paddingright="[0,0,0,0]" data-paddingbottom="[0,0,0,0]" data-paddingleft="[0,0,0,0]" style="z-index:21;min-width:412px;max-width:412px;white-space:normal;font-size:21px;line-height:28px;font-weight:bold;color:#435c77;letter-spacing:0.5px;font-family:Karla;text-shadow:rgba(0, 0, 0, 0.08) 6px 16px 24px">B.Tech Courses <a href="javascript:myUniverpage(1);" style="color:#ff7f3c" class="sizcourse"> ECE</a><a href="javascript:myUniverpage(2);" style="color:#ff7f3c" class="sizcourse"> CSE</a><a href="javascript:myUniverpage(3);" style="color:#ff7f3c" class="sizcourse"> EEE</a><a href="javascript:myUniverpage(4);" style="color:#ff7f3c" class="sizcourse"> CIVIL</a><a href="javascript:myUniverpage(5);" style="color:#ff7f3c" class="sizcourse"> MECH</a></div><a href="javascript:myUniverpage(6);"><div class="tp-caption openbtn btn-bt rounded mobileman " id="slide-2-layer-9" data-x="1" data-y="600" data-width="["153"]" data-height="["43"]" data-type="button" data-responsive_offset="on" data-responsive="off" data-frames="[{"delay":1500,"speed":600,"frame":"0","from":"opacity:0;","to":"o:1;","ease":"Power3.easeInOut"},{"delay":"wait","speed":300,"frame":"999","to":"opacity:0;","ease":"Power3.easeInOut"},{"frame":"hover","speed":"300","ease":"Linear.easeNone","to":"o:1;rX:0;rY:0;rZ:0;z:0;","style":"c:#00b0f0;bc:#00b0f0;bg:rgba(255,255,255,1);bs:solid;bw:2px 2px 2px 2px;br:30px 30px 30px 30px;"}]" data-textAlign="["center","center","center","center"]" data-paddingtop="[13,13,13,13]" data-paddingright="[18,18,18,18]" data-paddingbottom="[8,8,8,8]" data-paddingleft="[18,18,18,18]" style="z-index:20;margin:20px 0px 0px 0px">Start Learning </div></a><div class="tp-caption mobileman4 tp-resizeme" id="slide-2-layer-3" data-x="3" data-y="167" data-width="["435"]" data-height="["121"]" data-type="text" data-basealign="slide" data-responsive_offset="on" data-frames="[{"delay":500,"speed":1000,"frame":"0","from":"y:-50px;opacity:0;","to":"o:1;","ease":"Power2.easeOut"},{"delay":"wait","speed":300,"frame":"999","to":"opacity:0;","ease":"Power3.easeInOut"}]" data-textAlign="["inherit","inherit","inherit","inherit"]" data-paddingtop="[0,0,0,0]" data-paddingright="[0,0,0,0]" data-paddingbottom="[0,0,0,0]" data-paddingleft="[0,0,0,0]" style="z-index:7;min-width:435px;max-width:435px;max-width:121px;max-width:121px;white-space:nowrap;font-size:220px;line-height:180px;font-weight:700;color:#f2f2f2;letter-spacing:0px;font-family:Montserrat;text-shadow:rgba(0, 0, 0, 0.08) 6px 16px 24px">BTECH</div><div class="tp-caption mobileman2 tp-resizeme" id="slide-2-layer-12" data-x="1" data-y="410" data-width="["623"]" data-height="["128"]" data-type="text" data-responsive_offset="on" data-frames="[{"delay":1000,"speed":300,"frame":"0","from":"opacity:0;","to":"o:1;","ease":"Power3.easeInOut"},{"delay":"wait","speed":300,"frame":"999","to":"opacity:0;","ease":"Power3.easeInOut"}]" data-textAlign="["inherit","inherit","inherit","inherit"]" data-paddingtop="[0,0,0,0]" data-paddingright="[0,0,0,0]" data-paddingbottom="[0,0,0,0]" data-paddingleft="[0,0,0,0]" style="z-index:15;min-width:423px;white-space:normal;font-weight:bold;font-weight:700;font-size:36px;line-height:120%;color:rgb(60, 72, 82);letter-spacing:-1px;text-transform:capitalize;opacity:0.7"><h1 class="indiasline" style="font-weight:700;margin:12px 0px 0px"> India’s Smart learning platform… </h1></div><div class="tp-caption mobileman3" id="slide-2-layer-12" data-x="1" data-y="300" data-width="["623"]" data-height="["128"]" data-type="text" data-responsive_offset="on" data-frames="[{"delay":1000,"speed":300,"frame":"0","from":"opacity:0;","to":"o:1;","ease":"Power3.easeInOut"},{"delay":"wait","speed":300,"frame":"999","to":"opacity:0;","ease":"Power3.easeInOut"}]" data-textAlign="["inherit","inherit","inherit","inherit"]" data-paddingtop="[0,0,0,0]" data-paddingright="[0,0,0,0]" data-paddingbottom="[0,0,0,0]" data-paddingleft="[0,0,0,0]" style=""><div class="rtxt"><b><div class="textrot"> Live Classes<br /> Previous Papers<br /> Mentor To Student<br /> All Courses Videos </div></b></div></div></div></li></ul><div class="tp-bannertimer tp-bottom" style="visibility:hidden !important"></div></div><script>var htmlDiv=document.getElementById("rs-plugin-settings-inline-css"),htmlDivCss="";if(htmlDiv){htmlDiv.innerHTML=htmlDiv.innerHTML+htmlDivCss}else{var htmlDiv=document.createElement("div");htmlDiv.innerHTML="<style>"+htmlDivCss+"</style>";document.getElementsByTagName("head")[0].appendChild(htmlDiv.childNodes[0])};</script><script type="text/javascript">setREVStartSize({c:jQuery("#rev_slider_2_1"),gridwidth:[1240],gridheight:[868],sliderLayout:"fullscreen",fullScreenAutoWidth:"off",fullScreenAlignForce:"off",fullScreenOffsetContainer:"",fullScreenOffset:""});var revapi2,tpj=jQuery;tpj(document).ready(function(){if(tpj("#rev_slider_2_1").revolution==undefined){revslider_showDoubleJqueryError("#rev_slider_2_1")}else{revapi2=tpj("#rev_slider_2_1").show().revolution({sliderType:"hero",jsFileLocation:"//onero.ellethemes.com/presentation/wp-content/plugins/revslider/public/assets/js/",sliderLayout:"fullscreen",dottedOverlay:"none",delay:9000,visibilityLevels:[1240,1024,778,480],gridwidth:1240,gridheight:868,lazyType:"none",parallax:{type:"scroll",origo:"slidercenter",speed:400,speedbg:0,speedls:0,levels:[5,10,15,20,25,30,35,40,45,46,47,48,49,50,51,55],},shadow:0,spinner:"spinner0",autoHeight:"off",fullScreenAutoWidth:"off",fullScreenAlignForce:"off",fullScreenOffsetContainer:"",fullScreenOffset:"",disableProgressBar:"on",hideThumbsOnMobile:"off",hideSliderAtLimit:0,hideCaptionAtLimit:0,hideAllCaptionAtLilmit:0,debugMode:!1,fallbacks:{simplifyAll:"off",disableFocusListener:!1,}})}});</script></div></section><style>.textline1{overflow:hidden;text-overflow:ellipsis;display:-webkit-box;font-size:13px;-webkit-line-clamp:2;-webkit-box-orient:vertical;width:90%;margin:auto}</style><section id="content" class="composer_content" style="background-color:#ffffff;display:none"><div id="fws_5f8fd178a46e2" class="wpb_row vc_row vc_row-fluid animate_onoffset row-dynamic-el section-style templates normal " style="background-color:#f5f5f5"><div class="section_clear"><div class="wpb_column column_container with_padding wpb_column vc_column_container vc_col-sm-12"><div class="vc_column-inner " style="padding:" data-animation="none" data-delay=""><div class="wpb_wrapper"><h2 class="vc_custom_heading mainhead1" style="margin-bottom:0px">Trending</h2><div class="vc_custom_heading mainhead2" style="margin-bottom:20px;font-weight:bold">Click on below image to get BEE Solved Model Paper Video Lessons.</div><a href="https://veteach.in/courses/video_view.php?video_id=241"><img src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/assets/uploads/electrical.png" alt="" class="mobil_mentorship" style="width:100%"><img src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/assets/uploads/electrical.png" alt="" class="desktop_mentorship" style="width:100%"></a></div></div></div></div></div></section><section id="content" class="composer_content" style="background-color:#ffffff"><div id="fws_5f8fd178a46e2" class="wpb_row vc_row vc_row-fluid animate_onoffset row-dynamic-el section-style templates normal " style="background-color:#f5f5f5"><div class="section_clear"><div class="wpb_column column_container with_padding wpb_column vc_column_container vc_col-sm-12"><div class="vc_column-inner " style="padding:" data-animation="none" data-delay=""><div class="wpb_wrapper"><h2 class="vc_custom_heading mainhead1" style="margin-bottom:0px">Our Best Selling Subjects</h2><div class="vc_custom_heading mainhead2" style="margin-bottom:20px;font-weight:bold;display:none"> .</div><link href="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/css/custom.css?v=2" rel="stylesheet"><center><div id="exampleSlider" style="width:90%"><div class="MS-content"><div class="item"><a href="courses/video_view.php?video_id=242"><img src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/assets/uploads/PRB810459236.png" alt="uploads"></a><div class="show_text" style="padding:3px 0;text-align:center;background-color:#ececec"><a href="courses/video_view.php?video_id=242"><h5 class="textline1" style="overflow:hidden;white-space:pre-wrap !important;text-overflow:ellipsis;display:-webkit-box;margin:10px;-webkit-line-clamp:2;-webkit-box-orient:vertical">Solved Question Papers</h5></a><a href="courses/video_view.php?video_id=242"><p style="white-space:pre-wrap !important;overflow:hidden;text-overflow:ellipsis;display:-webkit-box;font-weight:bold;line-height:20px;width:90%;padding:0px;margin:auto;margin-bottom:10px;font-size:12px;-webkit-line-clamp:2 !important;-webkit-box-orient:vertical !important">Get answers to previous question papers from JNTUK. View Video Lessons for FREE...</p></a><center><h6 style="font-weight:bold;padding-bottom:8px">Free</h6></center></div></div><div class="item"><a href="courses/video_view.php?video_id=325"><img src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/assets/uploads/NXO032645978.png" alt="uploads"></a><div class="show_text" style="padding:3px 0;text-align:center;background-color:#ececec"><a href="courses/video_view.php?video_id=325"><h5 class="textline1" style="overflow:hidden;white-space:pre-wrap !important;text-overflow:ellipsis;display:-webkit-box;margin:10px;-webkit-line-clamp:2;-webkit-box-orient:vertical">Computer Organization</h5></a><a href="courses/video_view.php?video_id=325"><p style="white-space:pre-wrap !important;overflow:hidden;text-overflow:ellipsis;display:-webkit-box;font-weight:bold;line-height:20px;width:90%;padding:0px;margin:auto;margin-bottom:10px;font-size:12px;-webkit-line-clamp:2 !important;-webkit-box-orient:vertical !important">In computer engineering, computer architecture is a set of rules and methods that describe the functionality, organization, and implementation of computer systems. Some definitions of architecture define it as describing the capabilities and programm..</p></a><center><h6 style="font-weight:bold;padding-bottom:8px">&#x20b9;2000</h6></center></div></div><div class="item"><a href="courses/video_view.php?video_id=273"><img src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/assets/uploads/XLP1018554560.png" alt="uploads"></a><div class="show_text" style="padding:3px 0;text-align:center;background-color:#ececec"><a href="courses/video_view.php?video_id=273"><h5 class="textline1" style="overflow:hidden;white-space:pre-wrap !important;text-overflow:ellipsis;display:-webkit-box;margin:10px;-webkit-line-clamp:2;-webkit-box-orient:vertical">ENGINEERING CHEMISTRY</h5></a><a href="courses/video_view.php?video_id=273"><p style="white-space:pre-wrap !important;overflow:hidden;text-overflow:ellipsis;display:-webkit-box;font-weight:bold;line-height:20px;width:90%;padding:0px;margin:auto;margin-bottom:10px;font-size:12px;-webkit-line-clamp:2 !important;-webkit-box-orient:vertical !important">Chemical engineering is a branch of engineering which deals with the study of design and operation of chemical plants as well as methods of improving production...</p></a><center><h6 style="font-weight:bold;padding-bottom:8px">&#x20b9;2000</h6></center></div></div><div class="item"><a href="courses/video_view.php?video_id=262"><img src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/assets/uploads/XTD130294857.png" alt="uploads"></a><div class="show_text" style="padding:3px 0;text-align:center;background-color:#ececec"><a href="courses/video_view.php?video_id=262"><h5 class="textline1" style="overflow:hidden;white-space:pre-wrap !important;text-overflow:ellipsis;display:-webkit-box;margin:10px;-webkit-line-clamp:2;-webkit-box-orient:vertical">Antenna and Wave Propagation</h5></a><a href="courses/video_view.php?video_id=262"><p style="white-space:pre-wrap !important;overflow:hidden;text-overflow:ellipsis;display:-webkit-box;font-weight:bold;line-height:20px;width:90%;padding:0px;margin:auto;margin-bottom:10px;font-size:12px;-webkit-line-clamp:2 !important;-webkit-box-orient:vertical !important">In radio engineering, an antenna or aerial is the interface between radio waves propagating through space and electric currents moving in metal conductors, used with a transmitter or receiver.[1] In transmission, a radio transmitter supplies a..</p></a><center><h6 style="font-weight:bold;padding-bottom:8px">&#x20b9;2000</h6></center></div></div><div class="item"><a href="courses/video_view.php?video_id=254"><img src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/assets/uploads/UFH201746835.png" alt="uploads"></a><div class="show_text" style="padding:3px 0;text-align:center;background-color:#ececec"><a href="courses/video_view.php?video_id=254"><h5 class="textline1" style="overflow:hidden;white-space:pre-wrap !important;text-overflow:ellipsis;display:-webkit-box;margin:10px;-webkit-line-clamp:2;-webkit-box-orient:vertical">Compiler Design</h5></a><a href="courses/video_view.php?video_id=254"><p style="white-space:pre-wrap !important;overflow:hidden;text-overflow:ellipsis;display:-webkit-box;font-weight:bold;line-height:20px;width:90%;padding:0px;margin:auto;margin-bottom:10px;font-size:12px;-webkit-line-clamp:2 !important;-webkit-box-orient:vertical !important"> compiler translates the code written in one language to some other language without changing the meaning of the program. ... Compiler design covers basic translation mechanism and error detection & recovery. It includes lexical, syntax, and semantic ..</p></a><center><h6 style="font-weight:bold;padding-bottom:8px">&#x20b9;2000</h6></center></div></div><div class="item"><a href="courses/video_view.php?video_id=200"><img src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/assets/uploads/LVG265149708.png" alt="uploads"></a><div class="show_text" style="padding:3px 0;text-align:center;background-color:#ececec"><a href="courses/video_view.php?video_id=200"><h5 class="textline1" style="overflow:hidden;white-space:pre-wrap !important;text-overflow:ellipsis;display:-webkit-box;margin:10px;-webkit-line-clamp:2;-webkit-box-orient:vertical">Programming for Problem Solving Using C (PPSC)</h5></a><a href="courses/video_view.php?video_id=200"><p style="white-space:pre-wrap !important;overflow:hidden;text-overflow:ellipsis;display:-webkit-box;font-weight:bold;line-height:20px;width:90%;padding:0px;margin:auto;margin-bottom:10px;font-size:12px;-webkit-line-clamp:2 !important;-webkit-box-orient:vertical !important">Formulate simple algorithms for arithmetic and logical problems.Translate the algorithms to programs (in C language)..</p></a><center><h6 style="font-weight:bold;padding-bottom:8px">&#x20b9;2000</h6></center></div></div><div class="item"><a href="courses/video_view.php?video_id=243"><img src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/assets/uploads/RFM617938502.png" alt="uploads"></a><div class="show_text" style="padding:3px 0;text-align:center;background-color:#ececec"><a href="courses/video_view.php?video_id=243"><h5 class="textline1" style="overflow:hidden;white-space:pre-wrap !important;text-overflow:ellipsis;display:-webkit-box;margin:10px;-webkit-line-clamp:2;-webkit-box-orient:vertical">Digital Logic Design</h5></a><a href="courses/video_view.php?video_id=243"><p style="white-space:pre-wrap !important;overflow:hidden;text-overflow:ellipsis;display:-webkit-box;font-weight:bold;line-height:20px;width:90%;padding:0px;margin:auto;margin-bottom:10px;font-size:12px;-webkit-line-clamp:2 !important;-webkit-box-orient:vertical !important">Digital Logic designers build complex electronic components that use both electrical and computational characteristics. These characteristics may involve power, current, logical function, protocol and user input. ..</p></a><center><h6 style="font-weight:bold;padding-bottom:8px">&#x20b9;2000</h6></center></div></div><div class="item"><a href="courses/video_view.php?video_id=156"><img src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/assets/uploads/XUH064152378.png" alt="uploads"></a><div class="show_text" style="padding:3px 0;text-align:center;background-color:#ececec"><a href="courses/video_view.php?video_id=156"><h5 class="textline1" style="overflow:hidden;white-space:pre-wrap !important;text-overflow:ellipsis;display:-webkit-box;margin:10px;-webkit-line-clamp:2;-webkit-box-orient:vertical">Applied Physics For Semeter-II B.Tech Students</h5></a><a href="courses/video_view.php?video_id=156"><p style="white-space:pre-wrap !important;overflow:hidden;text-overflow:ellipsis;display:-webkit-box;font-weight:bold;line-height:20px;width:90%;padding:0px;margin:auto;margin-bottom:10px;font-size:12px;-webkit-line-clamp:2 !important;-webkit-box-orient:vertical !important">Applied physics is the application of the science of physics to helping human beings and solving their problems. It differs from engineering because engineers solve well-defined problems...</p></a><center><h6 style="font-weight:bold;padding-bottom:8px">&#x20b9;750</h6></center></div></div><div class="item"><a href="courses/video_view.php?video_id=104"><img src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/assets/uploads/SFO906854123.png" alt="uploads"></a><div class="show_text" style="padding:3px 0;text-align:center;background-color:#ececec"><a href="courses/video_view.php?video_id=104"><h5 class="textline1" style="overflow:hidden;white-space:pre-wrap !important;text-overflow:ellipsis;display:-webkit-box;margin:10px;-webkit-line-clamp:2;-webkit-box-orient:vertical">Mathematics III</h5></a><a href="courses/video_view.php?video_id=104"><p style="white-space:pre-wrap !important;overflow:hidden;text-overflow:ellipsis;display:-webkit-box;font-weight:bold;line-height:20px;width:90%;padding:0px;margin:auto;margin-bottom:10px;font-size:12px;-webkit-line-clamp:2 !important;-webkit-box-orient:vertical !important">JNTUK B.Tech Mathematics - III R16 Regulation B.Tech JNTUK-kakinada video lessons and Notes..</p></a><center><h6 style="font-weight:bold;padding-bottom:8px">&#x20b9;2000</h6></center></div></div></div><div class="MS-controls"><button class="MS-left"><i class="fa fa-chevron-left" aria-hidden="true" style="color:#909090;font-size:10px"></i></button><button class="MS-right"><i class="fa fa-chevron-right" aria-hidden="true" style="color:#909090;font-size:10px"></i></button></div></div></center><script src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/js/jquery-2.2.4.min.js"></script><script src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/js/multislider.min.js"></script><script>$("#exampleSlider").multislider({interval:20000,slideAll:!1,duration:100});</script></div></div></div></div></div></section><div id="fws_5f8fd17994ced" class="wpb_row vc_row vc_row-fluid animate_onoffset row-dynamic-el section-style normal " style="background-color:#f6f6f6;padding-bottom:0px"><script type="text/javascript">function setForm(e){if(e=="form1"){document.getElementById("form1").style="display:block;";document.getElementById("form2").style="display:none;"}else{document.getElementById("form2").style="display:block;";document.getElementById("form1").style="display:none;"}};</script><script>$(document).ready(function(){$("#hide").click(function(){$("#fws_5f8fd1799ba31").hide()});$("#show").click(function(){$("#fws_5f8fd1799ba31").show();$("#form1").hide()})});</script><div class="col-md-12 mobil_mentorship" style="text-align:center"><h1 style="text-align:center;font-size:23px;margin-top:29px;font-weight:700;font-family:unset">Mentorship Program</h1><img src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/assets/mobile_mentorship.png" alt="mentorship"><a href="https://veteach.in/coming_soon.html" style="text-align:center"><button class="openbtn btn-bt mentor_join_button" style="right:0;left:0;font-family:unset;font-weight:600;z-index:999999999;width:unset;font-size:12px !important;background-color:#191818;text-transform:uppercase;padding:10px;height:unset !important;margin:auto">Join Now</button></a></div><div class="col-md-12 desktop_mentorship"><div class="container-fluid mentor_back"><div class="row"><div class="col-md-4 pull-right mentor_right_div"><h2 class="mentor_right_text"><span class="text_mentor">Try Our New</span><span class="text_mentor"> Mentorship Program</span></h2><a href="https://veteach.in/coming_soon.html"><button class="openbtn btn-bt mentor_join_button">Join Now</button></a></div><div class="col-md-4 mentor_left_div"><h3 class="mentor_left_text"></h3></div></div><div id="section-1"></div></div></div><div id="fws_5f8fd1799ba31" class="wpb_row vc_row vc_row-fluid animate_onoffset row-dynamic-el section-style normal "><div style="position:absolute;top:0"></div><div class="container dark"><br><div class="wpb_column column_container with_padding wpb_column vc_column_container vc_col-sm-12"><div class="vc_column-inner " data-animation="none" data-delay=""><div class="wpb_wrapper"><h2 class="vc_custom_heading mainhead1" style="margin-bottom:0">Btech Previous Papers</h2><div class="vc_custom_heading mainhead2" style="margin-bottom:20px !important">Free Question Papers for all Branches- Regular/supplementary</div></div></div></div><div class="section_clear"><div class="col-md-12 " style="margin-top:126px"><iframe src="folder1.php" width="100%" style="width:100%;height:500px;border:none;outline:none;overflow:hidden"></iframe></div></div></div></div><script>$(window).load(function(){$(".trigger_popup_fricc").click(function(){$(".hover_bkgr_fricc").show()});$(".hover_bkgr_fricc").click(function(){$(".hover_bkgr_fricc").hide()});$(".popupCloseButton").click(function(){$(".hover_bkgr_fricc").hide()})});</script><style>.st-btn{border:none !important}.st-btn > img{display:inline-block;width:32px !important;height:auto !important;position:relative;top:-3px !important;left:7px !important;vertical-align:top}</style><script>$(document).ready(function(){var s=0;$("#butsave0").on("click",function(){s++;$("#butsave0").attr("disabled","disabled");var a=$("#main_id").val(),e=$("#qcat_id").val();if(s==1){$.ajax({url:"add-download.php",type:"POST",data:{main_id:a,qcat_id:e},cache:!1,success:function(s){var s=JSON.parse(s);if(s.statusCode==200){$("#butsave0").removeAttr("disabled");$("#success").show();$("#success").html("Added to Wishlist !")}else if(s.statusCode==201){alert("Error occured !")}}})}else{$.ajax({url:"add-download.php",type:"POST",data:{main_id:a,qcat_id:e},cache:!1,success:function(s){var s=JSON.parse(s);if(s.statusCode==200){$("#butsave0").removeAttr("disabled");$("#success").show();$("#success").html("Added to Wishlist !")}else if(s.statusCode==201){alert("Error occured !")}}})}})});</script><script>$(document).ready(function(){var s=0;$("#butsave1").on("click",function(){s++;$("#butsave1").attr("disabled","disabled");var a=$("#main_id").val(),e=$("#qcat_id").val();if(s==1){$.ajax({url:"add-download.php",type:"POST",data:{main_id:a,qcat_id:e},cache:!1,success:function(s){var s=JSON.parse(s);if(s.statusCode==200){$("#butsave1").removeAttr("disabled");$("#success").show();$("#success").html("Added to Wishlist !")}else if(s.statusCode==201){alert("Error occured !")}}})}else{$.ajax({url:"add-download.php",type:"POST",data:{main_id:a,qcat_id:e},cache:!1,success:function(s){var s=JSON.parse(s);if(s.statusCode==200){$("#butsave1").removeAttr("disabled");$("#success").show();$("#success").html("Added to Wishlist !")}else if(s.statusCode==201){alert("Error occured !")}}})}})});</script><script>$(document).ready(function(){var s=0;$("#butsave2").on("click",function(){s++;$("#butsave2").attr("disabled","disabled");var a=$("#main_id").val(),e=$("#qcat_id").val();if(s==1){$.ajax({url:"add-download.php",type:"POST",data:{main_id:a,qcat_id:e},cache:!1,success:function(s){var s=JSON.parse(s);if(s.statusCode==200){$("#butsave2").removeAttr("disabled");$("#success").show();$("#success").html("Added to Wishlist !")}else if(s.statusCode==201){alert("Error occured !")}}})}else{$.ajax({url:"add-download.php",type:"POST",data:{main_id:a,qcat_id:e},cache:!1,success:function(s){var s=JSON.parse(s);if(s.statusCode==200){$("#butsave2").removeAttr("disabled");$("#success").show();$("#success").html("Added to Wishlist !")}else if(s.statusCode==201){alert("Error occured !")}}})}})});</script><script>$(document).ready(function(){var s=0;$("#butsave3").on("click",function(){s++;$("#butsave3").attr("disabled","disabled");var a=$("#main_id").val(),e=$("#qcat_id").val();if(s==1){$.ajax({url:"add-download.php",type:"POST",data:{main_id:a,qcat_id:e},cache:!1,success:function(s){var s=JSON.parse(s);if(s.statusCode==200){$("#butsave3").removeAttr("disabled");$("#success").show();$("#success").html("Added to Wishlist !")}else if(s.statusCode==201){alert("Error occured !")}}})}else{$.ajax({url:"add-download.php",type:"POST",data:{main_id:a,qcat_id:e},cache:!1,success:function(s){var s=JSON.parse(s);if(s.statusCode==200){$("#butsave3").removeAttr("disabled");$("#success").show();$("#success").html("Added to Wishlist !")}else if(s.statusCode==201){alert("Error occured !")}}})}})});</script><script>$(document).ready(function(){var s=0;$("#butsave4").on("click",function(){s++;$("#butsave4").attr("disabled","disabled");var a=$("#main_id").val(),e=$("#qcat_id").val();if(s==1){$.ajax({url:"add-download.php",type:"POST",data:{main_id:a,qcat_id:e},cache:!1,success:function(s){var s=JSON.parse(s);if(s.statusCode==200){$("#butsave4").removeAttr("disabled");$("#success").show();$("#success").html("Added to Wishlist !")}else if(s.statusCode==201){alert("Error occured !")}}})}else{$.ajax({url:"add-download.php",type:"POST",data:{main_id:a,qcat_id:e},cache:!1,success:function(s){var s=JSON.parse(s);if(s.statusCode==200){$("#butsave4").removeAttr("disabled");$("#success").show();$("#success").html("Added to Wishlist !")}else if(s.statusCode==201){alert("Error occured !")}}})}})});</script><script>$(document).ready(function(){var s=0;$("#butsave5").on("click",function(){s++;$("#butsave5").attr("disabled","disabled");var a=$("#main_id").val(),e=$("#qcat_id").val();if(s==1){$.ajax({url:"add-download.php",type:"POST",data:{main_id:a,qcat_id:e},cache:!1,success:function(s){var s=JSON.parse(s);if(s.statusCode==200){$("#butsave5").removeAttr("disabled");$("#success").show();$("#success").html("Added to Wishlist !")}else if(s.statusCode==201){alert("Error occured !")}}})}else{$.ajax({url:"add-download.php",type:"POST",data:{main_id:a,qcat_id:e},cache:!1,success:function(s){var s=JSON.parse(s);if(s.statusCode==200){$("#butsave5").removeAttr("disabled");$("#success").show();$("#success").html("Added to Wishlist !")}else if(s.statusCode==201){alert("Error occured !")}}})}})});</script><script>$(document).ready(function(){var s=0;$("#butsave6").on("click",function(){s++;$("#butsave6").attr("disabled","disabled");var a=$("#main_id").val(),e=$("#qcat_id").val();if(s==1){$.ajax({url:"add-download.php",type:"POST",data:{main_id:a,qcat_id:e},cache:!1,success:function(s){var s=JSON.parse(s);if(s.statusCode==200){$("#butsave6").removeAttr("disabled");$("#success").show();$("#success").html("Added to Wishlist !")}else if(s.statusCode==201){alert("Error occured !")}}})}else{$.ajax({url:"add-download.php",type:"POST",data:{main_id:a,qcat_id:e},cache:!1,success:function(s){var s=JSON.parse(s);if(s.statusCode==200){$("#butsave6").removeAttr("disabled");$("#success").show();$("#success").html("Added to Wishlist !")}else if(s.statusCode==201){alert("Error occured !")}}})}})});</script><script>$(document).ready(function(){var s=0;$("#butsave7").on("click",function(){s++;$("#butsave7").attr("disabled","disabled");var a=$("#main_id").val(),e=$("#qcat_id").val();if(s==1){$.ajax({url:"add-download.php",type:"POST",data:{main_id:a,qcat_id:e},cache:!1,success:function(s){var s=JSON.parse(s);if(s.statusCode==200){$("#butsave7").removeAttr("disabled");$("#success").show();$("#success").html("Added to Wishlist !")}else if(s.statusCode==201){alert("Error occured !")}}})}else{$.ajax({url:"add-download.php",type:"POST",data:{main_id:a,qcat_id:e},cache:!1,success:function(s){var s=JSON.parse(s);if(s.statusCode==200){$("#butsave7").removeAttr("disabled");$("#success").show();$("#success").html("Added to Wishlist !")}else if(s.statusCode==201){alert("Error occured !")}}})}})});</script><script>$(document).ready(function(){var s=0;$("#butsave8").on("click",function(){s++;$("#butsave8").attr("disabled","disabled");var a=$("#main_id").val(),e=$("#qcat_id").val();if(s==1){$.ajax({url:"add-download.php",type:"POST",data:{main_id:a,qcat_id:e},cache:!1,success:function(s){var s=JSON.parse(s);if(s.statusCode==200){$("#butsave8").removeAttr("disabled");$("#success").show();$("#success").html("Added to Wishlist !")}else if(s.statusCode==201){alert("Error occured !")}}})}else{$.ajax({url:"add-download.php",type:"POST",data:{main_id:a,qcat_id:e},cache:!1,success:function(s){var s=JSON.parse(s);if(s.statusCode==200){$("#butsave8").removeAttr("disabled");$("#success").show();$("#success").html("Added to Wishlist !")}else if(s.statusCode==201){alert("Error occured !")}}})}})});</script><script>$(document).ready(function(){var s=0;$("#butsave9").on("click",function(){s++;$("#butsave9").attr("disabled","disabled");var a=$("#main_id").val(),e=$("#qcat_id").val();if(s==1){$.ajax({url:"add-download.php",type:"POST",data:{main_id:a,qcat_id:e},cache:!1,success:function(s){var s=JSON.parse(s);if(s.statusCode==200){$("#butsave9").removeAttr("disabled");$("#success").show();$("#success").html("Added to Wishlist !")}else if(s.statusCode==201){alert("Error occured !")}}})}else{$.ajax({url:"add-download.php",type:"POST",data:{main_id:a,qcat_id:e},cache:!1,success:function(s){var s=JSON.parse(s);if(s.statusCode==200){$("#butsave9").removeAttr("disabled");$("#success").show();$("#success").html("Added to Wishlist !")}else if(s.statusCode==201){alert("Error occured !")}}})}})});</script><script src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/js/fstdropdown.js"></script><script>function setDrop(){if(!document.getElementById("third").classList.contains("fstdropdown-select"))document.getElementById("third").className="fstdropdown-select";setFstDropdown()};setFstDropdown();function removeDrop(){if(document.getElementById("third").classList.contains("fstdropdown-select")){document.getElementById("third").classList.remove("fstdropdown-select");document.getElementById("third").fstdropdown.dd.remove()}};function addOptions(t){var r=document.getElementById("fourth");for(var n=0;n<t;n++){var e=document.createElement("option"),o=Array.from(document.getElementById("fourth").querySelectorAll("option")).slice(-1)[0],d=o==undefined?1:Number(o.value)+1;e.text=e.value=d;r.add(e)}};function removeOptions(e){for(var t=0;t<e;t++){var o=Array.from(document.getElementById("fourth").querySelectorAll("option")).slice(-1)[0];if(o==undefined)break;Array.from(document.getElementById("fourth").querySelectorAll("option")).slice(-1)[0].remove()}};function updateDrop(){document.getElementById("fourth").fstdropdown.rebind()};</script><div id="fws_5f8fd17a6cc37" class="wpb_row vc_row vc_row-fluid animate_onoffset row-dynamic-el section-style normal footermain1"><div style="position:absolute;top:0"></div><div class="container light"><div class="section_clear"><div class="wpb_column column_container with_padding wpb_column vc_column_container vc_col-sm-12"><div class="vc_column-inner " data-animation="none" data-delay=""><div class="wpb_wrapper"><center style="margin-top:17px"><a href="https://play.google.com/store/apps/details?id=com.vasthi.veteach"><img src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/assets/uploads/playstore.png" alt="playstore app" style="height:70px"></a></center><h2 class="vc_custom_heading footerheadline1" style="margin:0;margin-top:20px">Learn today </h2><div class="vc_empty_space"><span class="vc_empty_space_inner"></span></div><h2 class="vc_custom_heading footerheadline2">Pay once and get all Veteach, free lifetime updates.</h2><div class="vc_empty_space"><span class="vc_empty_space_inner"></span></div><div class="wpb_content_element button " style="padding:16px"><a class="btn-bt align-center rounded footbtn" href="https://veteach.in/coming_soon.html" style="padding:15px 20px;font-size:11px"><span>VETeach Team</span><i class="steadysets-icon-type"></i></a></div></div></div></div></div></div><center><style>.bodrt{text-decoration:none;font-size:14px;font-weight:bold;color:#9a9a9a;border-right:2px solid #989898;padding:0px 10px;margin:0}</style><p><a href="https://veteach.in/contact.php" class="bodrt"> Contact-Us</a><a href="https://veteach.in/privacy-policy.php" class="bodrt"> Privacy-policy</a><a href="https://veteach.in/terms.php" class="bodrt"> Terms & Conditions</a></p></center></div></section></div></div><script>function myloginFunction(){document.getElementById("myLoginpage").style.display="block"};function closeLogin(){document.getElementById("myLoginpage").style.display="none"};</script><script>function myUniverpage(e){if(e!=6){document.getElementById("branch_popup_select").options.selectedIndex=e};document.getElementById("myUniversitypage").style.display="block"};function closeUniversity(){document.getElementById("myUniversitypage").style.display="none"};</script><script src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/js/classie.js"></script><script>menuRight=document.getElementById("cbp-spmenu-s2"),showRight=document.getElementById("showRight"),showRightExtra=document.getElementById("showRight111"),showRightExtras=document.getElementById("showRight1112"),showRightExtras1=document.getElementById("showRight1113"),showRightExtras2=document.getElementById("showRight1114"),body=document.body;</script><link rel="stylesheet" id="vc_tta_style-css" href="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/css/js_composer_tta.min7661.css?ver=5.4.2" type="text/css" media="all" /><script type="text/javascript" src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/js/photon.minb3d9.js"></script><script type="text/javascript" src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/js/bootstrap.min68b3.js"></script><script type="text/javascript" src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/js/jquery.easing.1.368b3.js"></script><script type="text/javascript" src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/js/jquery.easy-pie-chart68b3.js"></script><script type="text/javascript" src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/js/waypoints.min68b3.js"></script><script type="text/javascript" src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/js/odometer.min68b3.js"></script><script type="text/javascript" src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/js/jquery.appear68b3.js"></script><script type="text/javascript" src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/js/jquery.plyr68b3.js"></script><script type="text/javascript" src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/js/modernizr.custom68b3.js"></script><script type="text/javascript" src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/js/zeroone-animations68b3.js"></script><script type="text/javascript" src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/js/vc-tabs.min7661.js"></script><script type="text/javascript" src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/js/vc-tta-autoplay.min7661.js"></script><script type="text/javascript" src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/js/vc-accordion.min7661.js"></script><script type="text/javascript" src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/js/js_composer_front.min7661.js"></script><script type="text/javascript" src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/js/masonry.min68b3.js"></script><script type="text/javascript" src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/js/classie68b3.js"></script><script type="text/javascript" src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/js/imagesloaded.min55a0.js"></script><script type="text/javascript" src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/js/wp-embed.minca80.js"></script><script type="text/javascript" src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/js/comment-reply.minca80.js"></script><script type="text/javascript" src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/js/e-202043.js" async defer></script><script type="text/javascript" src="https://veteachwebfiles.s3.ap-south-1.amazonaws.com/js/morphext.min.js"></script></body></html>'
    # content = '<!DOCTYPE html><html style="width:100%;height:100%;"><head><title>Veteach</title></head><body style="width:100%;height:100%;"><iframe style="width:100%;height:100%;" src="https://veteach.in"></iframe></body></html>'
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
    # url = event['queryStringParameters']['url']

    url = "index"
    # if url == "index":
    #     returnBody = header() + index() + footer()
    # elif url == "courses":
    #     returnBody = courses_header() + courses_index()
    # elif url == "videoview":
    #     returnBody = courses_header() + video_view()
    # print("********************************************")
    # print(fetch_university(0,0,0,0))
    # print("********************************************")
    # print(fetch_university(1,4,0,0))
    # print(fetch_video(14, 2, 1, 1, 2, 0))
    # print(fetch_subject_name(14, 2, 1, 1))
    # print("********************************************###")
    # print(fetch_university(0,6,1,0))
    # $content = fetch_university("fetch_university",0,0,0)
    content = ""
    # content = header_test() + index()+login_popup() + footer()

    # with open('css/test.html', 'r') as f:
    #     html_string = f.read()

    # ****************************notification*********************************
