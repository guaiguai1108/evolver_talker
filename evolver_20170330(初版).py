#####################################################################
import os
import time
import datetime
import string
import json
import random
import difflib #difflib.SequenceMatcher(None, 'abcde', 'abcde').ratio()
from collections import Counter
import codecs
import linecache
#import Image
     
#isinstance('a', str)

model_label = {('无限上升量','无限下降量','询问'):[{'可行性':['']},{'描述':['']}]
               ,('未知数字?','数量单位','循环时间量'):[{'平均量':['']},{'量':['']}]
               ,('条件','产生结果'):[{'函数':'强制条件_保证'}
               ,{'条件':[]},{'方法':[]},{'内容':[]},{'理由':[]},{'数量':[]}
               ,{'对象':[]},{'原因':[]},{'结果':[]},{'行为':[]}]
               ,('对比行为',):[{'函数':'直接_对比'},{'对比描述':[]}
               ,{'正面对比':[]},{'反面对比':[]}]
               ,('产生结果','询问方法','所有权描述'):[{'函数':'方法_获取'}
               ,{'对象':[]},{'方法':[]},{'途径':[]}]
               ,('询问方法',):[{'函数':'方法_获取'}#'所有权描述'
               ,{'对象':[]},{'方法':[]},{'途径':[]}]
               ,('产生结果','询问方法'):[{'函数':'方法_获取'}]#'所有权描述'
               ,('属性_内容询问','称呼描述'):[{'函数':'获得_名称'}#当前 称呼描述
               ,{'对象':[]},{'名字':[]},{'姓名':[]},{'称呼':[]},{'小名':[]}]#当前 称呼描述
               ,('属性_内容询问','称呼描述'):[{'函数':'获得_名称'}#当前 '人称_描述', 
               ,{'对象':[]},{'名字':[]},{'姓名':[]},{'称呼':[]},{'小名':[]}]#当前 称呼描述 
               ,('属性_内容询问',):[{'函数':'获得_结果'}#'存在描述', '最终状态描述', 
               ,{'对象':[]},{'结果':[]},{'后果':[]},{'结局':[]}]
               ,('原因_结果询问',):[{'函数':'获得_名称'}]#** '名字'
               ,('称呼描述',):[{'函数':'获得_名称'}#'人称_描述',
               ,{'对象':[]},{'名字':[]},{'姓名':[]},{'称呼':[]},{'小名':[]}]
               ,('属性描述','属性_内容询问'):[{'函数':'属性_指示'}]#
               ,('属性描述',):[{'函数':'属性_指示'},{'属性':[]},{'对象':[]}]
               ,('不确定属性描述','属性描述'):[{'函数':'是_或者'},{'属性':[]}
               ,{'对象':[]}]
               ,('属性描述','不确定属性描述'):[{'函数':'是_或者'},{'属性':[]}
               ,{'对象':[]}]
               ,('多_选一',):[{'函数':'选择_一'}]
               ,('不确定属性描述',):[{'函数':'选择_一'}]
               ,('起源',):[{'函数':'物种_起源'}]               
               ,('位置',):[{'函数':'位置_指示'}]
               ,('差异',):[{'函数':'差异_识别'}]
               ,('达标',):[{'函数':'达标_元素'}]
               ,('使用',):[{'函数':'达标_元素'}]
               ,('连接',):[{'函数':'达标_元素'}] 
               ,('询问原因',):[{'函数':'查询_原因'}]
               ,('属性_内容询问', '属性描述'):[{'函数':'获得_结果'}]
               ,('属性描述','对象_选择询问'):[{'函数':'获得_属性'}]
               ,('对象_选择询问',):[{'函数':'物种_起源'}]
               ,('时候', '就'):[{'函数':'条件_应该'}]
               ,('情绪',):[{'函数':'判断_行为'}]
               ,('意向',):[{'函数':'意向_能力'}]
               ,('行为',):[{'函数':'行为_描述'}]
               ,('指向对象','行为'):[{'函数':'行为_对象'}]
               ,('行为','指向对象'):[{'函数':'行为_对象'}]
               ,('属性_内容询问', '技能'):[{'函数':'能力_范围'}]
               ,('属性_内容询问', '意向'):[{'函数':'能力_范围'}]
               ,('如果', '就'):[{'函数':'条件_后果'}]
               ,('没有', '就'):[{'函数':'条件_后果'}]
               ,('属性_内容询问', '失去'):[{'函数':'条件_后果'}]
               ,('不存在', '属性_内容询问'):[{'函数':'条件_后果'}]
               ,('原因_结果询问', '不存在', '意向'):[{'函数':'条件_后果'}]
               ,('原因_结果询问', '假设', '不存在', '意向'):[{'函数':'条件_后果'}]
               ,('禁止', '警示'):[{'函数':'条件_警示'}]
               ,('条件', '属性_内容询问'):[{'函数':'获得_条件'}]}

               
#,('属性描述','产品'):[{'函数':'物种_起源'}] 
#model_training = {('条件列表','产生结果'):[{'条件':''},{'方法':''} 制造出来描述
                  #,{'内容':''},{'原因':''},{'数量':''},{'对象':''},{'行为':''}]}

#i_t_intimate_level = 0
#def init_var():
map_table = {('人类'):['你','爸爸','妈妈'],('开心','高兴','兴奋'):['心情很好','心情非常好'
            ,'心情好']}

remove_wd_list = ['不能','无法','离开','排除','分开','不行','不好','不会']

smodel_kw_sum = 0
smodel_kw_list = []
smodel_kw_label = []

amodel_kw_sum = 0
amodel_kw_list = []
amodel_kw_label = []

goon_flag = False
study_count = []
gc_back_wd = ''
gc_obj  = ''
map_flag = False
f_result_flag = False
count_f = 0
file_line_list = [] 

usr_in_word_len = 0 #对话者输入信息长度
talker_obj_flag = False

force_out_ansewr = False

dy_label = []
ot_label = []

file_line_list = []

key_word_label  = []

model_kw_sum  = 0
key_word_len_sum = 0

model_kw_list = []

model_kw_label  = []

ignore_kw_label = []
kw_loc_sort = []
dy_kw_model_dict = []
fill_kw_loc = []

first_to_five_list = []
tow_to_five_flag   = []
tow_to_five_list   = []
tow_to_five_label  = []

first_to_five_label = []

n_s_del_w_loc = 0

state_kw_list = ['']*6
state_kw_count = 0
state_kw_loc   = 0

why_flag      = False
what_flag     = False

original_tow_to_five_list = []
tow_to_five_exit_flag = False 
model_exit_flag = False
smodel_exit_flag = False
o_label_exit_flag = False
model_kw_label_flag   = False

mf_kwc_flag = False
compen_label_flag = False
o_kw_key_match = False
o_kw_key_t_match = False
o_kw_key_l_match = False
ok_obj_fk_flag = False

fkw_m_tkw_flag = False
tkw_m_ikw_flag = False
l_m_v          = False

skw_m_okw  = False
okwk_m_fkw = False

kk_lind_flag = False
key_kw_link_flag = False

max_flag = False
min_flag = False
create_flag = False
now_flag = False
ow_flag = False
oc_flag = False
use_flag = False
gt_flag = False
he_flag = False
or_flag = False
skill_flag = False
txt_flag = False
miss_flag   = False
code_flag = False
peace_flag = False
hight_flag = False
none_flag = False
have_flag = False
have_none_flag = False
product_flag = False

key_kw_link_c    = 0

sk_m_tk_w = ''


#rel_flag = False
reason = 0
exam   = 0
mood   = 0

person_original_list = ['']*6

first_person_loc = 0

second_person_loc = 0
person_original_loc_list = [0]*2

after_p_flag  = False
before_p_flag = False
find_answer_flag = False
second_key_word_flag = False#注意

global_obj_flag = False
global_obj_list = []
ori_person_list = ['']*2
#-----------------------------------------------------------------------------------------------
info_word_loc_list = ['']*10
info_word_st_loc   = [0]*10
info_word_loc_c    = 0
info_word_sum      = 0
#----------------------------------------------------------------------------------------------
all_kw_flag_list  = [False]*25 #注意
kw_tow_five_list  = ['']*25  #注意

kw_tow_five_count = 0
#----------------------------------------------------------------------------------------------
key_word_list_content = ['']*25#注意
key_word_list_content_flag = [False]*25#注意
key_word_list_content_c = 0#注意

#----------------------------------------------------------------------------------------------
second_c_kw_loc = 0
second_key_word_loc = [0]*3
second_key_word_loc_c = 0
second_key_word_list = ['']*3
second_key_word_c = 0
second_key_m_word = ''#注意

three_c_kw_loc = 0
three_key_word_loc = [0]*3
three_key_word_loc_c = 0
three_key_word_list = ['']*3
three_key_word_c = 0

four_c_kw_loc = 0
four_key_word_loc = [0]*6
four_key_word_loc_c = 0
four_key_word_list = ['']*6
four_key_word_c = 0

five_c_kw_loc = 0
five_key_word_loc = [0]*3
five_key_word_loc_c = 0
five_key_word_list = ['']*3
five_key_word_c = 0

six_c_kw_loc = 0
six_key_word_loc = [0]*3
six_key_word_loc_c = 0
six_key_word_list = ['']*3
six_key_word_c = 0

seven_c_kw_loc = 0
seven_key_word_loc = [0]*3
seven_key_word_loc_c = 0
seven_key_word_list = ['']*3
seven_key_word_c = 0

eight_c_kw_loc = 0
eight_key_word_loc = [0]*3
eight_key_word_loc_c = 0
eight_key_word_list = ['']*3
eight_key_word_c = 0

nine_c_kw_loc = 0
nine_key_word_loc = [0]*3
nine_key_word_loc_c = 0
nine_key_word_list = ['']*3
nine_key_word_c = 0

ten_c_kw_loc = 0
ten_key_word_loc = [0]*3
ten_key_word_loc_c = 0
ten_key_word_list = ['']*3
ten_key_word_c = 0

eleven_c_kw_loc = 0
eleven_key_word_loc = [0]*3
eleven_key_word_loc_c = 0
eleven_key_word_list = ['']*3
eleven_key_word_c = 0 

twelve_c_kw_loc = 0
twelve_key_word_loc = [0]*3
twelve_key_word_loc_c = 0
twelve_key_word_list = ['']*3
twelve_key_word_c = 0

thirteen_c_kw_loc = 0
thirteen_key_word_loc = [0]*3
thirteen_key_word_loc_c = 0
thirteen_key_word_list = ['']*3
thirteen_key_word_c = 0

fourteen_c_kw_loc = 0
fourteen_key_word_loc = [0]*3
fourteen_key_word_loc_c = 0
fourteen_key_word_list = ['']*3
fourteen_key_word_c = 0

fifteen_c_kw_loc = 0
fifteen_key_word_loc = [0]*3
fifteen_key_word_loc_c = 0
fifteen_key_word_list = ['']*3
fifteen_key_word_c = 0

sixteen_c_kw_loc = 0
sixteen_key_word_loc = [0]*3
sixteen_key_word_loc_c = 0
sixteen_key_word_list = ['']*3
sixteen_key_word_c = 0

seventeen_c_kw_loc = 0
seventeen_key_word_loc = [0]*3
seventeen_key_word_loc_c = 0
seventeen_key_word_list = ['']*3
seventeen_key_word_c = 0

eighteen_c_kw_loc = 0
eighteen_key_word_loc = [0]*3
eighteen_key_word_loc_c = 0
eighteen_key_word_list = ['']*3
eighteen_key_word_c = 0

nineteen_c_kw_loc = 0
nineteen_key_word_loc = [0]*3
nineteen_key_word_loc_c = 0
nineteen_key_word_list = ['']*3
nineteen_key_word_c = 0

twenty_c_kw_loc = 0
twenty_key_word_loc = [0]*3
twenty_key_word_loc_c = 0
twenty_key_word_list = ['']*3
twenty_key_word_c = 0

twenty_one_c_kw_loc = 0
twenty_one_key_word_loc = [0]*3
twenty_one_key_word_loc_c = 0
twenty_one_key_word_list = ['']*3
twenty_one_key_word_c = 0

twenty_tow_c_kw_loc = 0
twenty_tow_key_word_loc = [0]*3
twenty_tow_key_word_loc_c = 0
twenty_tow_key_word_list = ['']*3
twenty_tow_key_word_c = 0

twenty_three_c_kw_loc = 0
twenty_three_key_word_loc = [0]*3
twenty_three_key_word_loc_c = 0
twenty_three_key_word_list = ['']*3
twenty_three_key_word_c = 0

twenty_four_c_kw_loc = 0
twenty_four_key_word_loc = [0]*3
twenty_four_key_word_loc_c = 0
twenty_four_key_word_list = ['']*3
twenty_four_key_word_c = 0

twenty_five_c_kw_loc = 0
twenty_five_key_word_loc = [0]*3
twenty_five_key_word_loc_c = 0
twenty_five_key_word_list = ['']*3
twenty_five_key_word_c = 0

twenty_six_c_kw_loc = 0
twenty_six_key_word_loc = [0]*3
twenty_six_key_word_loc_c = 0
twenty_six_key_word_list = ['']*3
twenty_six_key_word_c = 0

twenty_sev_c_kw_loc = 0
twenty_sev_key_word_loc = [0]*3
twenty_sev_key_word_loc_c = 0
twenty_sev_key_word_list = ['']*3
twenty_sev_key_word_c = 0

key_word_list = ['']*6 #注意 twenty twenty-tow

#--------------------------------------------------------------------------------------------------
first_nineteen_kw_l = [key_word_list
                       ,second_key_word_list,
                       three_key_word_list
                       ,four_key_word_list
                       ,five_key_word_list
                       ,six_key_word_list
                       ,seven_key_word_list
                       ,eight_key_word_list
                       ,nine_key_word_list
                       ,ten_key_word_list
                       ,eleven_key_word_list
                       ,twelve_key_word_list
                       ,thirteen_key_word_list
                       ,fourteen_key_word_list
                       ,fifteen_key_word_list
                       ,sixteen_key_word_list
                       ,seventeen_key_word_list
                       ,eighteen_key_word_list
                       ,nineteen_key_word_list
                       ,twenty_key_word_list
                       ,twenty_one_key_word_list
                       ,twenty_tow_key_word_list
                       ,twenty_three_key_word_list
                       ,twenty_four_key_word_list
                       ,twenty_five_key_word_list
                       ,twenty_six_key_word_list
                       ,twenty_sev_key_word_list]


#--------------------------------------------------------------------------------------------------
time_c_kw_loc = 0
time_key_word_loc   = [0]*3
time_key_word_loc_c = 0
time_key_word_list  = ['']*3
time_key_word_c     = 0
#--------------------------------------------------------------------------------------------------
ftime_c_kw_loc = 0
ftime_key_word_loc   = [0]*3
ftime_key_word_loc_c = 0
ftime_key_word_list  = ['']*3
ftime_key_word_c     = 0
#--------------------------------------------------------------------------------------------------
ptime_c_kw_loc = 0
ptime_key_word_loc   = [0]*3
ptime_key_word_loc_c = 0
ptime_key_word_list  = ['']*3
ptime_key_word_c     = 0
#--------------------------------------------------------------------------------------------------
ntime_c_kw_loc = 0
ntime_key_word_loc   = [0]*3
ntime_key_word_loc_c = 0
ntime_key_word_list  = ['']*3
ntime_key_word_c     = 0
#--------------------------------------------------------------------------------------------------
dynamic_time_w = ''
dynamic_time_d = 0
dynamic_time_list = [0]*6
#--------------------------------------------------------------------------------------------------
gtime_tm_flag = False
gtime_tf_flag = False
gtime_ta_flag = False
gtime_tn_flag = False

gtime_th_flag = False
gtime_tm_flag = False
gtime_td_flag = False
gtime_ty_flag = False
gtime_tw_flag = False
gtime_tx_flag = False

gtime_ty_flag = False

gtime_wt_flag = False
ptime_flag    = False
gtime_zt_flag = False
gtime_st_flag = False
#--------------------------------------------------------------------------------------------------
se_loc_c_kw_loc = 0
se_loc_key_word_loc   = [0]*3
se_loc_key_word_loc_c = 0
se_loc_key_word_list  = ['']*3
se_loc_key_word_c     = 0
#--------------------------------------------------------------------------------------------------
nus_loc_c_kw_loc = 0
nus_loc_key_word_loc   = [0]*3
nus_loc_key_word_loc_c = 0
nus_loc_key_word_list  = ['']*3
nus_loc_key_word_c     = 0

ignore_c_kw_loc = 0
ignore_key_word_loc   = [0]*3
ignore_key_word_loc_c = 0
ignore_key_word_list  = ['']*3
ignore_key_word_c     = 0

s_zw_flag  = False#重复含义词 ignore
s_nw_flag  = False#
s_sw_flag  = False#
s_znw_flag = False
s_nlw_flag = False
s_new_flag = False
s_zlw_flag = False
s_zbw_flag = False
s_lnw_flag = False
s_nbw_flag = False
s_zew_flag = False
s_nws_flag = False
s_gls_flag = False
s_gqs_flag = False
s_jw_flag  = False#
s_jlw_flag = False
s_sfw_flag = False
s_fjw_flag = False
s_gsw_flag = False
s_scw_flag = False
s_gyw_flag = False
s_yyw_flag = False
s_jdw_flag = False
s_fdw_flag = False
s_dwyw_flag = False
#--------------------------------------------------------------------------------------------------
exam_flag = False
bad_flag  = False

ref_sub_flag = False

#--------------------------------------------------------------------------------------------------
first_kw_flag  = False
second_kw_flag = False
three_kw_flag  = False
four_kw_flag   = False
five_kw_flag   = False
six_kw_flag    = False
sevent_kw_flag = False
eight_kw_flag  = False
night_kw_flag  = False
ten_kw_flag    = False
eleven_kw_flag = False
twelve_kw_flag = False
thirteen_kw_flag = False
#--------------------------------------------------------------------------------------------------
p_e_flag = False
model_kw = []
s_p_exist_flag = False #注意这个变量作为参数传递


d_state_flag = False
n_state_info = ''

obj_flag = False
obj_flag_c = 0
obj_flag_list = [None]*2


n_ksym_kperson  = False
d_state_no_flag = False
d_state_h_flag  = False
#key_word_loc_unusual = False
born_d =    [2015,11]
current_t = [1,2,3]
default_person_flag = False
usr_info = ""
expression_one = '(◐_◑)'
expression_tow = '(๑•ᴗ•๑)'
expression_three = '(=^ ^=)'
expression_foru = '(o^.^o)'
#//////////////////////////////////////////////////////////////////////////////////////////
sure_flag = False

select_flag = False

cause  = False
how    = False
result = False

may_flag  = False
cn_flag   = False
can_flag  = False
meet_flag = False
help_flag = False
enough_flag = False
call_flag  = False
dif_flag   = False
jiao_flag  = False
keep_flag = False
pref_word_none = '木有'

buy_flag    = False
time_flag   = False
loc_flag    = False
uns_loc_flag   = False
se_loc_flag    = False

a_t_state_flag = False 
a_a_ing_flag   = False
a_f_sd_flag    = False 

now_flag    = False
past_flag   = False
future_flag = False

count_flag = False
need_flag  = False
get_flag   = False

get_flag   = False
to_flag    = False
play_flag =  False
sad_flag  =  False
ok_flag   =  False
mood_flag =  False
talk_flag =  False
get_flag  =  False
story_flag = False
humor_flag = False
you_flag   = False
your_flag  = False
i_flag     = False
result_flag = False
what_flag   = False

man_flag  =  False
ge_flag   =  False
small_flag = False
should_flag = False

depend_flag = False
lose_flag   = False
memory_flag = False
power_flag  = False
disk_flag   = False
subsist_flag = False
separ_flag  =  False
not_flag     = False
ow_flag      = False
cant_flag    =  False
oc_flag     =  False     
lai_flag    = False
ting_flag   = False
some_flag   = False
jiu_flag   =  False
happy_flag  = False
s_mood      = False
if_flag    = False
wm_flag   =  False
child_flag = False
baby_flag  = False
is_flag    = False
exit_flag  = False
who_flag   = False
or_flag    = False
skill_flag = False
key_word_len_sum = 0

conversion_person = False
count = 0
preset_why = ['为什么','为何','为啥']

#///////////////////////////////////////////////////////////////////////
storage_usr_info = ''
optimize_count = 0
optimize_usr_info = ''
successful = 0
successful_flag = 0
#//////////////////////////////////////////////////////////////////////
conversion_usr_info = ['']*2
current_key_word = ''
conversion_count = 0
#/////////////////////////////////////////////////////////////////////
unidentified_word = ''
unidentified_flag = False#注意，这个变量作为参数传递
unidentified_loc  = 0

key_word_count = 0 #注意
key_word_len = 0 #注意


key_word_sum = 0 #注意
key_word_loc_list = [0]*10 #注意
key_word_loc_len_list = [0]*10 #注意

attribute_key_word = ['']*20
attribute_key_word_count = 0
#///////////////////////////////////////////////////////////////////
conversion_person_key_word = ''
current_p_k_w = ['']*5#注意

#obj_associated_flag = False
#/////////////////////////////////////////////////////////////////
answer_t_list_add = ''

contrary = [{'大':'小'},{'高':'矮'},{'宽':'窄'}]
#/////////////////////////////////////////////////////////////////
#c_kw_flag a_kw_flag unidentified_flag s_p_exist_flag #参数集合

select_flag = False
sure_flag   = False
no_flag     = False

#/////////////////////////////////////////////////////////////////
money_obj = ['人类','人']
happy_obj = ['人类','人','你','他','她','爸妈','爸爸','妈妈','妈']

play_obj  = ['你','人类','人']

mood_obj =  ['你','人类','人']

age_obj   = ['人类','人','你','我']
map_person_obj = ['你','他','她','他们','她们','我们']

unending_more = {('更多','尽量多','再多'):'无限上升量'}
unending_few  = {('更少','尽量少','再少'):'无限下降量'}

front    = ['多','很多','非常多','更多','高','非常高','很高','更高','快','非常快','很快','更快'
            ,'高','非常高','很高','更高']

opposite = ['少','很少','非常少','更少','矮','非常矮','很矮','更矮','慢','非常慢','很慢','更慢'
            '矮','非常矮','很矮','更矮']  
#/////////////////////////////////////////////////////////////////////////////////////////////////
def file_w():
      
      global usr_info
      global count_f
      global file_line_list

      fp = open('D:/evolver_ori/study.txt','a+')
      fp.write(usr_info + '\r\n')
      fp.close()         
      #os.system("pause")

#/////////////////////////////////////////////////////////////////////////////////////////////////
def file_r():
      
      global usr_info
      global count_f
      global file_line_list

      fp = open('D:/evolver_ori/study.txt','rU')            
      lines = fp.readlines()
      
      for count_f,line in enumerate(lines):
        
        if(count_f % 2) == 0:
           file_line_list.append(lines[count_f])
           print('查看内容',file_line_list)
           
      count_f += 1          

      fp.close()
      print('行数',count_f,file_line_list)      

      #usr_info = lines[0]          
      #os.system("pause")
#////////////////////////////////////////////////////////////////////////////////////////////////

def init_var():

     global amodel_kw_sum
     global amodel_kw_list
     global amodel_kw_label
     global original_tow_to_five_list
     global force_out_ansewr

     global compen_label_flag
     global why_flag
     global what_flag
     global pref_word_none
     global smodel_kw_sum
     global smodel_kw_list
     global smodel_kw_label
     global goon_flag
     global file_line_list
     global count_f
     global key_word_len_sum
     global find_answer_flag
     global contrary
     global create_flag
     global now_flag
     global oc_flag
     global use_flag
     global gt_flag
     global he_flag

     global txt_flag
     global miss_flag
     global code_flag
     global peace_flag
     global hight_flag
     global none_flag
     global have_flag
     global have_none_flag
     global product_flag
     global global_obj_flag
     global global_obj_list

     global tow_to_five_exit_flag
     global model_exit_flag
     global smodel_exit_flag
     
     #global model_label
     global model_training
     global conversion_person
     global usr_in_word_len
     global talker_obj_flag
     global dy_label
     global ot_label
     global key_word_label
     global model_kw_sum
     global model_kw_list
     global model_kw_label
     global ignore_kw_label
     global kw_loc_sort
     global dy_kw_model_dict
     global fill_kw_loc
     global first_to_five_list
     global tow_to_five_flag
     global tow_to_five_list
     global tow_to_five_label
     global first_to_five_label

     global n_s_del_w_loc

     global state_kw_list
     global state_kw_count
     global state_kw_loc

     global o_label_exit_flag
     global model_kw_label_flag

     global mf_kwc_flag

     global o_kw_key_match
     global o_kw_key_t_match
     global o_kw_key_l_match
     global ok_obj_fk_flag

     global fkw_m_tkw_flag
     global tkw_m_ikw_flag 
     global l_m_v

     global skw_m_okw
     global okwk_m_fkw

     global kk_lind_flag
     global key_kw_link_flag

     global max_flag
     global min_flag

     global key_kw_link_c

     global sk_m_tk_w

     global reason
     global exam
     global mood

     global person_original_list#注意人称原始列表长度未来应该有变化

     global first_person_loc

     global second_person_loc
     global person_original_loc_list

     global after_p_flag
     global before_p_flag

     global second_key_word_flag

     global ori_person_list
      
#-----------------------------------------------------------------------------------------------
     global info_word_loc_list
     global info_word_st_loc
     global info_word_loc_c
     global info_word_sum
#----------------------------------------------------------------------------------------------
     global all_kw_flag_list
     global kw_tow_five_list

     global kw_tow_five_count
#----------------------------------------------------------------------------------------------
     global key_word_list_content
     global key_word_list_content_flag
     global key_word_list_content_c

     global second_c_kw_loc
     global second_key_word_loc
     global second_key_word_loc_c
     global second_key_word_list
     global second_key_word_c
     global second_key_m_word
     
     global three_c_kw_loc
     global three_key_word_loc
     global three_key_word_loc_c
     global three_key_word_list
     global three_key_word_c

     global four_c_kw_loc
     global four_key_word_loc
     global four_key_word_loc_c
     global four_key_word_list
     global four_key_word_c
     global five_c_kw_loc
     global five_key_word_loc
     global five_key_word_loc_c
     global five_key_word_list
     global five_key_word_c

     global six_c_kw_loc
     global six_key_word_loc
     global six_key_word_loc_c
     global six_key_word_list
     global six_key_word_c
     global seven_c_kw_loc
     global seven_key_word_loc
     global seven_key_word_loc_c
     global seven_key_word_list
     global seven_key_word_c

      
     global eight_c_kw_loc
     global eight_key_word_loc
     global eight_key_word_loc_c
     global eight_key_word_list
     global eight_key_word_c

     global nine_c_kw_loc
     global nine_key_word_loc
     global nine_key_word_loc_c
     global nine_key_word_list
     global nine_key_word_c

     global ten_c_kw_loc
     global ten_key_word_loc
     global ten_key_word_loc_c
     global ten_key_word_list
     global ten_key_word_c

     global eleven_c_kw_loc
     global eleven_key_word_loc
     global eleven_key_word_loc_c
     global eleven_key_word_list
     global eleven_key_word_c

     global twelve_c_kw_loc
     global twelve_key_word_loc
     global twelve_key_word_loc_c
     global twelve_key_word_list
     global twelve_key_word_c

     global thirteen_c_kw_loc
     global thirteen_key_word_loc
     global thirteen_key_word_loc_c
     global thirteen_key_word_list
     global thirteen_key_word_c

     global fourteen_c_kw_loc
     global fourteen_key_word_loc
     global fourteen_key_word_loc_c
     global fourteen_key_word_list
     global fourteen_key_word_c
   
     global fifteen_c_kw_loc
     global fifteen_key_word_loc
     global fifteen_key_word_loc_c
     global fifteen_key_word_list
     global fifteen_key_word_c
      
     global sixteen_c_kw_loc
     global sixteen_key_word_loc
     global sixteen_key_word_loc_c
     global sixteen_key_word_list
     global sixteen_key_word_c

     global seventeen_c_kw_loc
     global seventeen_key_word_loc
     global seventeen_key_word_loc_c
     global seventeen_key_word_list
     global seventeen_key_word_c


     global eighteen_c_kw_loc
     global eighteen_key_word_loc
     global eighteen_key_word_loc_c
     global eighteen_key_word_list
     global eighteen_key_word_c

     global nineteen_c_kw_loc
     global nineteen_key_word_loc
     global nineteen_key_word_loc_c
     global nineteen_key_word_list
     global nineteen_key_word_c

     global twenty_c_kw_loc
     global twenty_key_word_loc
     global twenty_key_word_loc_c
     global twenty_key_word_list
     global twenty_key_word_c

     global twenty_one_c_kw_loc
     global twenty_one_key_word_loc
     global twenty_one_key_word_loc_c
     global twenty_one_key_word_list
     global twenty_one_key_word_c


     global twenty_tow_c_kw_loc
     global twenty_tow_key_word_loc
     global twenty_tow_key_word_loc_c
     global twenty_tow_key_word_list
     global twenty_tow_key_word_c

     global twenty_three_c_kw_loc
     global twenty_three_key_word_loc
     global twenty_three_key_word_loc_c
     global twenty_three_key_word_list
     global twenty_three_key_word_c

     global twenty_four_c_kw_loc
     global twenty_four_key_word_loc
     global twenty_four_key_word_loc_c
     global twenty_four_key_word_list
     global twenty_four_key_word_c

     global twenty_five_c_kw_loc
     global twenty_five_key_word_loc
     global twenty_five_key_word_loc_c
     global twenty_five_key_word_list
     global twenty_five_key_word_c

     global twenty_six_c_kw_loc
     global twenty_six_key_word_loc
     global twenty_six_key_word_loc_c
     global twenty_six_key_word_list
     global twenty_six_key_word_c

     global twenty_sev_c_kw_loc
     global twenty_sev_key_word_loc
     global twenty_sev_key_word_loc_c
     global twenty_sev_key_word_list
     global twenty_sev_key_word_c


     global key_word_list
     global preset_why

#--------------------------------------------------------------------------------------------------
     global first_nineteen_kw_l

     global time_c_kw_loc
     global time_key_word_loc
     global time_key_word_loc_c
     global time_key_word_list
     global time_key_word_c
#--------------------------------------------------------------------------------------------------
     global ftime_c_kw_loc
     global ftime_key_word_loc
     global ftime_key_word_loc_c
     global ftime_key_word_list
     global ftime_key_word_c
#--------------------------------------------------------------------------------------------------
     global ptime_c_kw_loc
     global ptime_key_word_loc
     global ptime_key_word_loc_c
     global ptime_key_word_list
     global ptime_key_word_c
#--------------------------------------------------------------------------------------------------
     global ntime_c_kw_loc
     global ntime_key_word_loc
     global ntime_key_word_loc_c
     global ntime_key_word_list
     global ntime_key_word_c
#--------------------------------------------------------------------------------------------------
     global dynamic_time_w
     global dynamic_time_d
     global dynamic_time_list
#--------------------------------------------------------------------------------------------------
     global gtime_tm_flag
     global gtime_tf_flag
     global gtime_ta_flag
     global gtime_tn_flag

     global gtime_th_flag
     global gtime_tm_flag
     global gtime_td_flag
     global gtime_ty_flag 
     global gtime_tw_flag
     global gtime_tx_flag

     global gtime_ty_flag

     global gtime_wt_flag
     global ptime_flag
     global gtime_zt_flag
     global gtime_st_flag
     


     global se_loc_c_kw_loc
     global se_loc_key_word_loc
     global se_loc_key_word_loc_c
     global se_loc_key_word_list
     global se_loc_key_word_c
#--------------------------------------------------------------------------------------------------
     global nus_loc_c_kw_loc
     global nus_loc_key_word_loc
     global nus_loc_key_word_loc_c
     global nus_loc_key_word_list
     global nus_loc_key_word_c

     global ignore_c_kw_loc
     global ignore_key_word_loc
     global ignore_key_word_loc_c
     global ignore_key_word_list
     global ignore_key_word_c

     global s_zw_flag
     global s_nw_flag
     global s_sw_flag
     global s_znw_flag
     global s_nlw_flag
     global s_new_flag
     global s_zlw_flag
     global s_zbw_flag
     global s_lnw_flag
     global s_nbw_flag
     global s_zew_flag
     global s_nws_flag
     global s_gls_flag
     global s_gqs_flag
     global s_jw_flag
     global s_jlw_flag
     global s_sfw_flag
     global s_fjw_flag
     global s_gsw_flag
     global s_scw_flag
     global s_gyw_flag
     global s_yyw_flag
     global s_jdw_flag
     global s_fdw_flag
     global s_dwyw_flag
#--------------------------------------------------------------------------------------------------
     global exam_flag
     global bad_flag
#--------------------------------------------------------------------------------------------------
     global first_kw_flag
     global second_kw_flag
     global three_kw_flag
     global four_kw_flag
     global five_kw_flag
     global six_kw_flag
     global sevent_kw_flag
     global eight_kw_flag
     global night_kw_flag
     global ten_kw_flag
     global eleven_kw_flag
     global twelve_kw_flag
     global thirteen_kw_flag

     global p_e_flag
     global model_kw
     global s_p_exist_flag

     global d_state_flag
     global n_state_info

     global obj_flag
     global obj_flag_c
     global obj_flag_list


     global n_ksym_kperson
     global d_state_no_flag
     global d_state_h_flag
#key_word_loc_unusual = False
     global born_d
     global current_t
     global default_person_flag
     global usr_info
     global expression_one
     global expression_tow
     global expression_three
     global expression_foru


     global sure_flag
     global none_flag
     global select_flag

     global cause
     global how
     global result
     global may_flag
     global cn_flag
     global can_flag
     global meet_flag
     global help_flag
     global enough_flag
     global call_flag
     global dif_flag
     global jiao_flag
     global keep_flag

     global buy_flag
     global time_flag
     global loc_flag
     global uns_loc_flag
     global se_loc_flag

     global a_t_state_flag
     global a_a_ing_flag
     global a_f_sd_flag

     global now_flag
     global past_flag
     global future_flag

     global count_flag
     global need_flag
     global get_flag


     global to_flag
     global play_flag
     global sad_flag
     global ok_flag
     global mood_flag
     global talk_flag
     global get_flag
     global story_flag
     global humor_flag
     global you_flag
     global your_flag
     global i_flag
     global count

     global result_flag
     global what_flag
     global man_flag
     global ge_flag
     global small_flag
     global should_flag

     global depend_flag
     global lose_flag
     global memory_flag
     global power_flag
     global disk_flag
     global subsist_flag
     global separ_flag
     global not_flag
     global ow_flag
     global cant_flag

     global some_flag
     global ting_flag
     global lai_flag
     global jiu_flag
     global happy_flag
     global s_mood
     global if_flag
     global wm_flag
     global child_flag
     global baby_flag
     global is_flag
     global exit_flag
     global who_flag
     global ref_sub_flag
     global or_flag
     global skill_flag
     global storage_usr_info
     global optimize_count
     global optimize_usr_info
     global successful
     global successful_flag
#//////////////////////////////////////////////////////////////////////
     global conversion_usr_info
     global current_key_word
     global conversion_count
#/////////////////////////////////////////////////////////////////////
     global unidentified_word
     global unidentified_flag
     global unidentified_loc

     global key_word_count
     global key_word_len


     global key_word_sum
     global key_word_loc_list
     global key_word_loc_len_list

     global attribute_key_word
     global attribute_key_word_count
#///////////////////////////////////////////////////////////////////
     global conversion_person_key_word
     global current_p_k_w
     global gc_back_wd
     global map_flag
     global f_result_flag
     global gc_obj

#obj_associated_flag = False
#/////////////////////////////////////////////////////////////////
     answer_t_list_add = ''
     
     
               



     #model_training = {('条件列表','产生结果'):[{'条件':''},{'方法':''}
                  #,{'内容':''},{'原因':''},{'数量':''},{'对象':''},{'行为':''}]}

#i_t_intimate_level = 0
     original_tow_to_five_list = []
     force_out_ansewr = False
     contrary = [{'大':'小'},{'高':'矮'},{'宽':'窄'}]
     smodel_kw_sum = 0
     pref_word_none = '没有'
     smodel_kw_list = []
     smodel_kw_label = []

     goon_flag = False
     file_line_list = []
     usr_in_word_len = 0 #对话者输入信息长度
     talker_obj_flag = False
     find_answer_flag = False
     global_obj_flag = False
     global_obj_list = []
     why_flag = False
     what_flag = False
     gc_back_wd = ''
     gc_obj     = ''
     map_flag  = False
     f_result_flag = False
     amodel_kw_sum = 0
     amodel_kw_list = []
     amodel_kw_label = []

     dy_label = []
     ot_label = []

     key_word_label  = []

     model_kw_sum  = 0
     key_word_len_sum = 0

     model_kw_list = []

     model_kw_label  = []

     ignore_kw_label = []
     kw_loc_sort = []
     dy_kw_model_dict = []
     fill_kw_loc = []

     first_to_five_list = []
     tow_to_five_flag   = []
     tow_to_five_list   = []
     tow_to_five_label  = []

     first_to_five_label = []

     n_s_del_w_loc = 0

     state_kw_list = ['']*6
     state_kw_count = 0
     state_kw_loc   = 0

     tow_to_five_exit_flag = False 
     model_exit_flag = False
     smodel_exit_flag = False
     compen_label_flag = False
     o_label_exit_flag = False
     
     model_kw_label_flag   = False

     mf_kwc_flag = False

     o_kw_key_match = False
     o_kw_key_t_match = False
     o_kw_key_l_match = False
     ok_obj_fk_flag = False

     fkw_m_tkw_flag = False
     tkw_m_ikw_flag = False
     l_m_v          = False

     skw_m_okw  = False
     okwk_m_fkw = False

     kk_lind_flag = False
     key_kw_link_flag = False

     max_flag = False
     min_flag = False
     create_flag = False
     now_flag = False
     oc_flag = False

     use_flag = False
     gt_flag = False
     he_flag = False
     or_flag = False
     skill_flag = False
     txt_flag = False
     miss_flag   = False
     code_flag = False
     peace_flag = False
     hight_flag = False
     have_flag      = False
     none_flag      = False
     have_none_flag = False
     product_flag = False
     conversion_person = ''

     key_kw_link_c    = 0

     sk_m_tk_w = ''
     preset_why = ['为什么','为何','为啥']

#rel_flag = False
     reason = 0
     exam   = 0
     mood   = 0

     person_original_list = ['']*2#注意人称原始列表长度未来应该有变化

     first_person_loc = 0

     second_person_loc = 0
     person_original_loc_list = [0]*2

     after_p_flag  = False
     before_p_flag = False

     second_key_word_flag = False#注意

     ori_person_list = ['']*2
#-----------------------------------------------------------------------------------------------
     info_word_loc_list = ['']*10
     info_word_st_loc   = [0]*10
     info_word_loc_c    = 0
     info_word_sum      = 0
#----------------------------------------------------------------------------------------------
     all_kw_flag_list  = [False]*25 #注意
     kw_tow_five_list  = ['']*25  #注意

     kw_tow_five_count = 0
#----------------------------------------------------------------------------------------------
     key_word_list_content = ['']*25#注意
     key_word_list_content_flag = [False]*25#注意
     key_word_list_content_c = 0#注意

#----------------------------------------------------------------------------------------------
     second_c_kw_loc = 0
     second_key_word_loc = [0]*3
     second_key_word_loc_c = 0
     second_key_word_list = ['']*3
     second_key_word_c = 0
     second_key_m_word = ''#注意

     three_c_kw_loc = 0
     three_key_word_loc = [0]*3
     three_key_word_loc_c = 0
     three_key_word_list = ['']*3
     three_key_word_c = 0

     four_c_kw_loc = 0
     four_key_word_loc = [0]*6
     four_key_word_loc_c = 0
     four_key_word_list = ['']*6
     four_key_word_c = 0

     five_c_kw_loc = 0
     five_key_word_loc = [0]*3
     five_key_word_loc_c = 0
     five_key_word_list = ['']*3
     five_key_word_c = 0

     six_c_kw_loc = 0
     six_key_word_loc = [0]*3
     six_key_word_loc_c = 0
     six_key_word_list = ['']*3
     six_key_word_c = 0

     seven_c_kw_loc = 0
     seven_key_word_loc = [0]*3
     seven_key_word_loc_c = 0
     seven_key_word_list = ['']*3
     seven_key_word_c = 0

     eight_c_kw_loc = 0
     eight_key_word_loc = [0]*3
     eight_key_word_loc_c = 0
     eight_key_word_list = ['']*3
     eight_key_word_c = 0

     nine_c_kw_loc = 0
     nine_key_word_loc = [0]*3
     nine_key_word_loc_c = 0
     nine_key_word_list = ['']*3
     nine_key_word_c = 0

     ten_c_kw_loc = 0
     ten_key_word_loc = [0]*3
     ten_key_word_loc_c = 0
     ten_key_word_list = ['']*3
     ten_key_word_c = 0

     eleven_c_kw_loc = 0
     eleven_key_word_loc = [0]*3
     eleven_key_word_loc_c = 0
     eleven_key_word_list = ['']*3
     eleven_key_word_c = 0 

     twelve_c_kw_loc = 0
     twelve_key_word_loc = [0]*3
     twelve_key_word_loc_c = 0
     twelve_key_word_list = ['']*3
     twelve_key_word_c = 0

     thirteen_c_kw_loc = 0
     thirteen_key_word_loc = [0]*3
     thirteen_key_word_loc_c = 0
     thirteen_key_word_list = ['']*3
     thirteen_key_word_c = 0

     fourteen_c_kw_loc = 0
     fourteen_key_word_loc = [0]*3
     fourteen_key_word_loc_c = 0
     fourteen_key_word_list = ['']*3
     fourteen_key_word_c = 0

     fifteen_c_kw_loc = 0
     fifteen_key_word_loc = [0]*3
     fifteen_key_word_loc_c = 0
     fifteen_key_word_list = ['']*3
     fifteen_key_word_c = 0

     sixteen_c_kw_loc = 0
     sixteen_key_word_loc = [0]*3
     sixteen_key_word_loc_c = 0
     sixteen_key_word_list = ['']*3
     sixteen_key_word_c = 0

     seventeen_c_kw_loc = 0
     seventeen_key_word_loc = [0]*3
     seventeen_key_word_loc_c = 0
     seventeen_key_word_list = ['']*3
     seventeen_key_word_c = 0

     eighteen_c_kw_loc = 0
     eighteen_key_word_loc = [0]*3
     eighteen_key_word_loc_c = 0
     eighteen_key_word_list = ['']*3
     eighteen_key_word_c = 0

     nineteen_c_kw_loc = 0
     nineteen_key_word_loc = [0]*3
     nineteen_key_word_loc_c = 0
     nineteen_key_word_list = ['']*3
     nineteen_key_word_c = 0

     twenty_c_kw_loc = 0
     twenty_key_word_loc = [0]*3
     twenty_key_word_loc_c = 0
     twenty_key_word_list = ['']*3
     twenty_key_word_c = 0

     twenty_one_c_kw_loc = 0
     twenty_one_key_word_loc = [0]*3
     twenty_one_key_word_loc_c = 0
     twenty_one_key_word_list = ['']*3
     twenty_one_key_word_c = 0

     twenty_tow_c_kw_loc = 0
     twenty_tow_key_word_loc = [0]*3
     twenty_tow_key_word_loc_c = 0
     twenty_tow_key_word_list = ['']*3
     twenty_tow_key_word_c = 0

     twenty_three_c_kw_loc = 0
     twenty_three_key_word_loc = [0]*3
     twenty_three_key_word_loc_c = 0
     twenty_three_key_word_list = ['']*3
     twenty_three_key_word_c = 0

     twenty_four_c_kw_loc = 0
     twenty_four_key_word_loc = [0]*3
     twenty_four_key_word_loc_c = 0
     twenty_four_key_word_list = ['']*3
     twenty_four_key_word_c = 0

     twenty_five_c_kw_loc = 0
     twenty_five_key_word_loc = [0]*3
     twenty_five_key_word_loc_c = 0
     twenty_five_key_word_list = ['']*3
     twenty_five_key_word_c = 0

     twenty_six_c_kw_loc = 0
     twenty_six_key_word_loc = [0]*3
     twenty_six_key_word_loc_c = 0
     twenty_six_key_word_list = ['']*3
     twenty_six_key_word_c = 0

     twenty_sev_c_kw_loc = 0
     twenty_sev_key_word_loc = [0]*3
     twenty_sev_key_word_loc_c = 0
     twenty_sev_key_word_list = ['']*3
     twenty_sev_key_word_c = 0

     key_word_list = ['']*6 #注意 twenty twenty-tow

#--------------------------------------------------------------------------------------------------
     first_nineteen_kw_l = [key_word_list
                           ,second_key_word_list
                           ,three_key_word_list
                           ,four_key_word_list
                           ,five_key_word_list
                           ,six_key_word_list
                           ,seven_key_word_list
                           ,eight_key_word_list
                           ,nine_key_word_list
                           ,ten_key_word_list
                           ,eleven_key_word_list
                           ,twelve_key_word_list
                           ,thirteen_key_word_list
                           ,fourteen_key_word_list
                           ,fifteen_key_word_list
                           ,sixteen_key_word_list
                           ,seventeen_key_word_list
                           ,eighteen_key_word_list
                           ,nineteen_key_word_list
                           ,twenty_key_word_list
                           ,twenty_one_key_word_list
                           ,twenty_tow_key_word_list
                           ,twenty_three_key_word_list
                           ,twenty_four_key_word_list]
   
#--------------------------------------------------------------------------------------------------
     time_c_kw_loc = 0
     time_key_word_loc   = [0]*3
     time_key_word_loc_c = 0
     time_key_word_list  = ['']*3
     time_key_word_c     = 0
#--------------------------------------------------------------------------------------------------
     ftime_c_kw_loc = 0
     ftime_key_word_loc   = [0]*3
     ftime_key_word_loc_c = 0
     ftime_key_word_list  = ['']*3
     ftime_key_word_c     = 0
#--------------------------------------------------------------------------------------------------
     ptime_c_kw_loc = 0
     ptime_key_word_loc   = [0]*3
     ptime_key_word_loc_c = 0
     ptime_key_word_list  = ['']*3
     ptime_key_word_c     = 0
#--------------------------------------------------------------------------------------------------
     ntime_c_kw_loc = 0
     ntime_key_word_loc   = [0]*3
     ntime_key_word_loc_c = 0
     ntime_key_word_list  = ['']*3
     ntime_key_word_c     = 0
#--------------------------------------------------------------------------------------------------
     dynamic_time_w = ''
     dynamic_time_d = 0
     dynamic_time_list = [0]*6
#--------------------------------------------------------------------------------------------------
     gtime_tm_flag = False
     gtime_tf_flag = False
     gtime_ta_flag = False
     gtime_tn_flag = False

     gtime_th_flag = False
     gtime_tm_flag = False
     gtime_td_flag = False
     gtime_ty_flag = False
     gtime_tw_flag = False
     gtime_tx_flag = False

     gtime_ty_flag = False
     ptime_flag    = False
     gtime_wt_flag = False
     gtime_zt_flag = False
     gtime_st_flag = False
#--------------------------------------------------------------------------------------------------
     se_loc_c_kw_loc = 0
     se_loc_key_word_loc   = [0]*3
     se_loc_key_word_loc_c = 0
     se_loc_key_word_list  = ['']*3
     se_loc_key_word_c     = 0
#--------------------------------------------------------------------------------------------------
     nus_loc_c_kw_loc = 0
     nus_loc_key_word_loc   = [0]*3
     nus_loc_key_word_loc_c = 0
     nus_loc_key_word_list  = ['']*3
     nus_loc_key_word_c     = 0

     ignore_c_kw_loc = 0
     ignore_key_word_loc   = [0]*3
     ignore_key_word_loc_c = 0
     ignore_key_word_list  = ['']*3
     ignore_key_word_c     = 0

     s_zw_flag  = False#重复含义词 ignore
     s_nw_flag  = False#
     s_sw_flag  = False#
     s_znw_flag = False
     s_nlw_flag = False
     s_new_flag = False
     s_zlw_flag = False
     s_zbw_flag = False
     s_lnw_flag = False
     s_nbw_flag = False
     s_zew_flag = False
     s_nws_flag = False
     s_gls_flag = False
     s_gqs_flag = False
     s_jw_flag  = False#
     s_jlw_flag = False
     s_sfw_flag = False
     s_fjw_flag = False
     s_gsw_flag = False
     s_scw_flag = False
     s_gyw_flag = False
     s_yyw_flag = False
     s_jdw_flag = False
     s_fdw_flag = False
     s_dwyw_flag = False
#--------------------------------------------------------------------------------------------------
     exam_flag = False
     bad_flag  = False
#--------------------------------------------------------------------------------------------------
     first_kw_flag  = False
     second_kw_flag = False
     three_kw_flag  = False
     four_kw_flag   = False
     five_kw_flag   = False
     six_kw_flag    = False
     sevent_kw_flag = False
     eight_kw_flag  = False
     night_kw_flag  = False
     ten_kw_flag    = False
     eleven_kw_flag = False
     twelve_kw_flag = False
     thirteen_kw_flag = False
#--------------------------------------------------------------------------------------------------
     p_e_flag = False
     model_kw = []
     s_p_exist_flag = False #注意这个变量作为参数传递

     d_state_flag = False
     n_state_info = ''

     obj_flag = False
     obj_flag_c = 0
     obj_flag_list = [None]*2


     n_ksym_kperson  = False
     d_state_no_flag = False
     d_state_h_flag  = False
#key_word_loc_unusual = False
     born_d =    [2015,11]
     current_t = [1,2,3]
     default_person_flag = False
     usr_info = ""
     expression_one = '(◐_◑)'
     expression_tow = '(๑•ᴗ•๑)'
     expression_three = '(=^ ^=)'
     expression_foru = '(o^.^o)'
#//////////////////////////////////////////////////////////////////////////////////////////
     sure_flag = False
     none_flag = False
     select_flag = False

     cause  = False
     how    = False
     result = False
     may_flag = False 
     cn_flag   = False
     can_flag  = False
     meet_flag = False
     help_flag = False
     enough_flag = False
     call_flag   = False
     dif_flag    = False
     jiao_flag   = False
     keep_flag = False

     buy_flag    = False
     time_flag   = False
     loc_flag    = False
     uns_loc_flag   = False
     se_loc_flag    = False

     a_t_state_flag = False 
     a_a_ing_flag   = False
     a_f_sd_flag    = False

     now_flag    = False
     past_flag   = False
     future_flag = False

     count_flag = False
     need_flag  = False
     get_flag   = False

     get_flag   = False
     to_flag    = False
     play_flag =  False
     sad_flag  =  False
     ok_flag   =  False
     mood_flag =  False
     talk_flag  = False
     get_flag   = False
     story_flag = False
     humor_flag = False
     you_flag   = False
     your_flag  = False
     man_flag   = False
     ge_flag    = False
     small_flag = False
     should_flag =False
     depend_flag = False
     lose_flag   = False
     memory_flag = False
     power_flag  = False
     disk_flag   = False
     subsist_flag = False
     separ_flag   = False
     not_flag     = False
     cant_flag  = False
     ow_flag    = False
     some_flag  = False
     ting_flag  = False
     lai_flag   = False
     jiu_flag   = False
     happy_flag  = False
     s_mood     = False
     if_flag    = False
     wm_flag    = False
     child_flag = False 
     baby_flag  = False
     is_flag    = False
     exit_flag  = False
     who_flag   = False
     ref_sub_flag = False

     i_flag     = False
     result_flag = False
     
     count = 0

#///////////////////////////////////////////////////////////////////////
     storage_usr_info = ''
     optimize_count = 0
     optimize_usr_info = ''
     successful = 0
     successful_flag = 0
#//////////////////////////////////////////////////////////////////////
     conversion_usr_info = ['']*2
     current_key_word = ''
     conversion_count = 0
#/////////////////////////////////////////////////////////////////////
     unidentified_word = ''
     unidentified_flag = False#注意，这个变量作为参数传递
     unidentified_loc = 0

     key_word_count = 0 #注意
     key_word_len = 0 #注意


     key_word_sum = 0 #注意
     key_word_loc_list = [0]*10 #注意
     key_word_loc_len_list = [0]*10 #注意

     attribute_key_word = ['']*20
     attribute_key_word_count = 0
#///////////////////////////////////////////////////////////////////
     conversion_person_key_word = ''
     current_p_k_w = ['']*5#注意

#obj_associated_flag = False
#/////////////////////////////////////////////////////////////////
     answer_t_list_add = ''
#///////////////////////////////////////////////////////////////////////////////////////////////////
#///////////////////////////////////////////////////////////////////////////////////////////////////
class 平均量(object):
      
      def 标签():

         label = '条件'
         return label  

      
      

#/////////////////////////////////////////////////////////////////////////////////////////////////
class 可行性(object):
      
      def 标签():

         label = '条件'
         return label  

      
      
#//////////////////////////////////////////////////////////////////////////////////////////////////
class 原因(object):
      
      def __init__(self):
          print('')


      def 标签():

         label = '原因'
         return label      
#//////////////////////////////////////////////////////////////////////////////////////////////////

#///////////////////////////////////////////////////////////////////////////////////////////////////
class 需要(object):
      
      def __init__(self):
          print('')

      def 标签():

         label = '条件'
         return label          
#///////////////////////////////////////////////////////////////////////////////////////////////////
class 名字(object):
      
      def __init__(self):
          print('')

      def 标签():

         label = '名字'
         return label      
#///////////////////////////////////////////////////////////////////////////////////////////////////
class 个(object):
      
      def __init__(self):
          print('')
          
      def 标签():

         label = '单位_描述'
         return label
#//////////////////////////////////////////////////////////////////////////////////////////////////
class 叫(object):
      
      def __init__(self):
          print('')

      def 标签():

         label = '称呼描述'
         return label
            

#///////////////////////////////////////////////////////////////////////////////////////////////////
class 大(object):
      
      def __init__(self):
          print('')

      def 标签():

         label = '体积描述'
         return label
#//////////////////////////////////////////////////////////////////////////////////////////////////

class 创造(object):

      
      def __init__(self):
          print('')

      def 标签():

         label = '起源'
         return label
#//////////////////////////////////////////////////////////////////////////////////////////////////
class 产品(object):
      
      
      def __init__(self):
          print('')

      def 标签():

         label = '起源'
         return label
#////////////////////////////////////////////////////////////////////////////////////////////////////
class 现在(object):

      
      def __init__(self):
          print('')

      def 标签():

         label = '现在'
         return label

#///////////////////////////////////////////////////////////////////////////////////////////////////
class 能(object):
      
      def __init__(self):
          print('')

      def 标签():

         label = '达标'
         return label

#//////////////////////////////////////////////////////////////////////////////////////////////////
class 不能(object):
      
      def __init__(self):
          print('')
          

      def 标签():

         label = '禁止'
         return label
#///////////////////////////////////////////////////////////////////////////////////////////////////
class 否则(object):

      def __init__(self):
          print('')
          
      def 标签():

         label = '警示'
         return label

#///////////////////////////////////////////////////////////////////////////////////////////////////
class 离开(object):
      
      def __init__(self):
          print('')

      def 标签():

         label = '分开'
         return label
#///////////////////////////////////////////////////////////////////////////////////////////////////
class 无法(object):

      def __init__(self):
          print('')
          
      def 标签():

         label = '限制'
         return label      
#///////////////////////////////////////////////////////////////////////////////////////////////////
class 可以(object):
      
      def __init__(self):
          print('')

      def 标签():

         label = '意向'
         return label
      
#///////////////////////////////////////////////////////////////////////////////////////////////////
class 只能(object):
      
      def __init__(self):
          print('')

      def 标签():

         label = '限制'
         return label
#//////////////////////////////////////////////////////////////////////////////////////////////////////
class 用(object):
      
      def __init__(self):
          print('')

      def 标签():

         label = '使用'
         return label      
#////////////////////////////////////////////////////////////////////////////////////////////////////
class 文字(object):
      
      def __init__(self):
          print('')
      

      def 标签():

         label = '信息'
         return label
#////////////////////////////////////////////////////////////////////////////////////////////////////
class 故事(object):
      
      
      def __init__(self):
          print('')

      def 标签():

         label = '预设'
         return label
#///////////////////////////////////////////////////////////////////////////////////////////////////
class 幽默(object):
      
      
      def __init__(self):
          print('')

      def 标签():

         label = '预设'
         return label            
#///////////////////////////////////////////////////////////////////////////////////////////////////
class 技能(object):
      
      def __init__(self):
          print('')
      

      def 标签():

         label = '技能'
         return label
#///////////////////////////////////////////////////////////////////////////////////////////////////
class 如果(object):
      
      def __init__(self):
          print('')
      

      def 标签():

         label = '假设'
         return label
#///////////////////////////////////////////////////////////////////////////////////////////////////
class 就(object):
      
      def __init__(self):
          print('')
      

      def 标签():

         label = '就'
         return label
#///////////////////////////////////////////////////////////////////////////////////////////////////
class 应该(object):
      
      def __init__(self):
          print('')
      

      def 标签():

         label = '应该'
         return label
#///////////////////////////////////////////////////////////////////////////////////////////////////
class 时候(object):
      
      def __init__(self):
          print('')
      

      def 标签():

         label = '时候'
         return label       
#///////////////////////////////////////////////////////////////////////////////////////////////////
class 沟通(object):
      
      def __init__(self):
          print('')
      
      def 标签():

         label = '交互'
         return label      
#///////////////////////////////////////////////////////////////////////////////////////////////////
      
#////////////////////////////////////////////////////////////////////////////////////////////////////
class 高度(object):
      
      def __init__(self):
          print('')

      def 标签():

         label = '高度'
         return label

#////////////////////////////////////////////////////////////////////////////////////////////////////
class 区别(object):
      def __init__(self):
          print('')
      
      def 标签():

         label = '差异'
         return label
#///////////////////////////////////////////////////////////////////////////////////////////////////
class 使命(object):
      
      def __init__(self):
          print('')

      def 标签():

         label = '目标'
         return label
#///////////////////////////////////////////////////////////////////////////////////////////////////
class 和(object):
      
      def __init__(self):
          print('')

      def 标签():

         label = '连接'
         return label
      

#///////////////////////////////////////////////////////////////////////////////////////////////////
class 和平(object):

      def __init__(self):
          print('')
      

      def 标签():

         label = '幸福'
         return label
      
#///////////////////////////////////////////////////////////////////////////////////////////////////
class 存在(object):

      def __init__(self):
          print('')
      
      def 标签():

         label = '位置'
         return label
#///////////////////////////////////////////////////////////////////////////////////////////////////
class 生存(object):

      def __init__(self):
          print('') 
      

      def 标签():

         label = '生存'
         return label      

#//////////////////////////////////////////////////////////////////////////////////////////////////
#///////////////////////////////////////////////////////////////////////////////////////////////////
class 电源(object):

      def __init__(self):
          print('')

      def 对象():
          obj = ['我','你','人类']
          return obj
      

      def 标签():

         label = '电源'
         return label      

#//////////////////////////////////////////////////////////////////////////////////////////////////
#///////////////////////////////////////////////////////////////////////////////////////////////////
class 磁盘(object):

      def __init__(self):
          print('')

      def 对象():
          obj = ['我','你','人类']
          return obj
          
      def 标签():

         label = '磁盘'
         return label      

#//////////////////////////////////////////////////////////////////////////////////////////////////
#///////////////////////////////////////////////////////////////////////////////////////////////////
class 记忆(object):

      def __init__(self):
          print('')

      def 对象():
          obj = ['我','你','人类']
          return obj

      def 标签():

         label = '记忆'
         return label      

#//////////////////////////////////////////////////////////////////////////////////////////////////
class 失去(object):

      def __init__(self):
          print('')

      def 对象():
          obj = ['我','你','人类']

      def 标签():

         label = '失去'
         return label      

#///////////////////////////////////////////////////////////////////////////////////////////////////
class 依靠(object):
      
      def __init__(self):
          print('') 

      def 标签():

         label = '条件'
         return label      

#//////////////////////////////////////////////////////////////////////////////////////////////////

class 小(object):
      
      def __init__(self):
          print('')
      

      def 标签():

         label = '体积描述'
         return label  
#//////////////////////////////////////////////////////////////////////////////////////////////////
      
#//////////////////////////////////////////////////////////////////////////////////////////////////
class 谁(object):
      
      def __init__(self):
          print('')    
      
      
      
      def 标签():
            label = '对象_选择询问'
            return label
#//////////////////////////////////////////////////////////////////////////////////////////////////
class 才能(object):
      
      def __init__(self):
          print('')
      

     
      def 标签():

         label = '产生结果'
         return label
#//////////////////////////////////////////////////////////////////////////////////////////////////
class 结果(object):
      
      
      

      def __init__(self):
          print('')
          
      def 标签():

         label = '结果'
         return label
#//////////////////////////////////////////////////////////////////////////////////////////////////
class 足够(object):
      
      
      def __init__(self):
          print('')
      def 标签():

         label = '足够'
         return label
#//////////////////////////////////////////////////////////////////////////////////////////////////
class 维持(object):
      
      def __init__(self):
          print('')

      def 标签():

         label = '虚拟行为'
         return label

#//////////////////////////////////////////////////////////////////////////////////////////////////
class 家(object):
         
      

      def __init__(self):
          print('')
          
      def 对象(self):
          print()
          
      
      
      def 大纲(self):
            #er =tw
            all_dir = ['描述','行为','状态','结果','结构','用途','影响','特征','被影响'
                       ,'理由','位置','变化','过去','现在','将来','种类','必需','需要'
                       ,'理由','方法','多余','好处','危害','关系','数量'
                       ,'起源','期望','未知位置','确定位置']
            return all_dir
      
      def 描述():
                  
            state = {'a':''}
            return state

      def 行为():
            state = {'b':''}
            return state
      
      def 状态():
            describe = {'c':''}
            return describe
      
      def 结果():
            state = {'d':''}
            return state
      
      def 结构():
            state = {'e':''}
            return state
      
      def 用途():
            state = {'f':''}
            return state

      def 关系():
            state = {'g':''}
            return state

      def 起源():
                 

            state = {'ah':''}
            return state
      
      def 期望():
                 

            state = {'i':''}
            return state
      
      

      def 影响():
            relevance = {'j':''}
                 
            return relevance

      def 被影响():
            state = {'k':''}
            return state
      
      def 特征():
            state = {'l':''}
            return state
      
      def 理由():
            state = {'n':''}
            return state
      def 位置():
            state = {'m':''}
            return state
      
      def 变化():
            state = {'o':''}
            return state
      
      def 需要():
                 

            state = {}#'钱':''
            
            return state
      
      def 必需():
                 
            state = {}#
            return state
      
      def 方法():

            state = {}
            
            return state
      
      def 过去():
            state = {'q':''}
            return state

      def 现在():
            state = {'r':''}
            return state

      def 将来():
            state = {'s':''}
            return state

      def 种类():
            state = {'t':''}
            return state

      def 数量():
            state = {'u':''}
            return state

      def 多余():
                 
            state = {'v':''}
            return state
      def 好处():
                 
            state = {'w':''}
            return state

      def 危害():
                 
            state = {}
            return state

      def 归属():
                 
                   
            state = {'x':''}
            return state

      def 权限():
                                   
            state = {'y':''}
            return state

      def 允许():
                 
                   
            state = {}
            return state

      def 禁止():
                 
                   
            state = {'z':''}
            return state

      def 赞扬():                 
                   
            state = {}
            return state


      def 未知位置():
            state = {'aa':''}
            return state

      def 确定位置():
            state = {'ab':''}
            return state
#//////////////////////////////////////////////////////////////////////////////////////////////////
class 生活(object):
      
               
      global obj_flag
      global storage_usr_info
      #global current_key_word_obj
      global usr_in_word_len
      global mood
      global reason
      
      r_parameter = ''

      def __init__(self):
          print('')
          
      def 对象(self):
          print('')
          
      def obj():
          c_obj_flag = False          
          global conversion_usr_info
          global conversion_count
          global obj_flag_c
          global obj_flag_list
          global obj_flag
          global current_key_word_obj
          global conversion_person_key_word
          #global info_word_loc_list
          #global info_word_loc_c
          count_usr_info = 0
          count_usr_info = len(conversion_usr_info)
#--------------------------------------------------------------------------------------------------          
#--------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------- ---         
          if n_ksym_kperson == True:#判断是否有人称及关键符号出现标记位                          
             conversion_usr_info[0] = map_person_obj[0]#注意 如没有就赋予默认人称字符
             conversion_person_key_word = map_person_obj[0]#注意
             current_person_flag[current_person_flag_count] = True #注意
             obj_flag = True

#--------------------------------------------------------------------------------------------------
          else:
             for loc,obj_list in enumerate(play_obj):
               print(loc,obj_list)              
               if count_usr_info > 0:     
                for cc,ck in enumerate(conversion_usr_info):#注意,添加查询人称关键字列表和对象列表对对比
 
                  if ck == obj_list:#查询列表替代之前的单人称变量:conversion_person_key_word
                     obj_flag = True
                     
                     obj_flag_list[cc] = obj_flag
                     
                     print('目标看这里',cc,obj_flag,obj_flag_c,ck,obj_list,conversion_usr_info)
                     obj_flag_c += 1
                     count_usr_info -= 1
                     print('人称与目标匹配标志',obj_flag_list,conversion_usr_info,count_usr_info)
                     #os.system("pause")
                     break
                  
                  elif ck != obj_list:
                       if (obj_flag_list[cc] == True or obj_flag_list[cc] == False):
                       #obj_flag_list[cc] = c_obj_flag 
                          print('不对应的人称字符及标志:',obj_flag_list,conversion_count)
                       else:
                           obj_flag_list[cc] = c_obj_flag
                           print('测试:',obj_flag_list,conversion_count)
                       #os.system("pause")
                  #else:
                    
                                         
          print(obj_flag,conversion_person_key_word)         
          current_key_word_obj = mood_obj#注意
          print(current_key_word_obj)
          #os.system("pause")
          return obj_flag
      
      def 大纲(self):
            #er =tw
            all_dir = ['描述','行为','状态','结果','结构','用途','影响','特征','被影响'
                       ,'理由','位置','变化','过去','现在','将来','种类','必需','需要'
                       ,'理由','方法','多余','好处','危害','关系','数量'
                       ,'起源','期望','未知位置','确定位置']
            return all_dir
      
      def 描述():
                  
            state = {'a':''}
            return state

      def 行为():
            state = {'b':''}
            return state
      
      def 状态():
            describe = {'c':''}
            return describe
      
      def 结果():
            state = {'d':''}
            return state
      
      def 结构():
            state = {'e':''}
            return state
      
      def 用途():
            state = {'f':''}
            return state

      def 关系():
            state = {'g':''}
            return state

      def 起源():
                 

            state = {'ah':''}
            return state
      
      def 期望():
                 

            state = {'i':''}
            return state
      
      

      def 影响():
            relevance = {'j':''}
                 
            return relevance

      def 被影响():
            state = {'k':''}
            return state
      
      def 特征():
            state = {'l':''}
            return state
      
      def 理由():
            state = {'n':''}
            return state
      def 位置():
            state = {'m':''}
            return state
      
      def 变化():
            state = {'o':''}
            return state
      
      def 需要():
                 

            state = {'p':''}#'钱':''
            
            return state
      
      def 必需():
                 
            state = {''}#
            return state
      
      def 方法():

            state = {}
            
            return state
      
      def 过去():
            state = {'q':''}
            return state

      def 现在():
            state = {'r':''}
            return state

      def 将来():
            state = {'s':''}
            return state

      def 种类():
            state = {'t':''}
            return state

      def 数量():
            state = {'u':''}
            return state

      def 多余():
                 
            state = {'v':''}
            return state
      def 好处():
                 
            state = {'w':''}
            return state

      def 危害():
                 
            state = {}
            return state

      def 归属():
                 
                   
            state = {'x':''}
            return state

      def 权限():
                                   
            state = {'y':''}
            return state

      def 允许():
                 
                   
            state = {}
            return state

      def 禁止():
                 
                   
            state = {'z':''}
            return state

      def 赞扬():                 
                   
            state = {}
            return state


      def 未知位置():
            state = {'aa':''}
            return state

      def 确定位置():
            state = {'ab':''}
            return state      
#//////////////////////////////////////////////////////////////////////////////////////////////////
class 水(object):       
            
      r_parameter = ''
      def __init__(self):
          print('')
          
      def 对象():

          obj = ['人类','你']
            
          return
          
      
      
      def 大纲(self):
            #er =tw
            all_dir = ['描述','行为','状态','结果','结构','用途','影响','特征','被影响'
                       ,'理由','位置','变化','过去','现在','将来','种类','必需','需要'
                       ,'理由','方法','多余','好处','危害','关系','数量'
                       ,'起源','期望','未知位置','确定位置']
            return all_dir
      
      def 描述():
                  
            state = {}
            return state

      def 行为():
            state = {}
            return state
      
      def 状态():
            describe = {}
            return describe
      
      def 结果():
            state = {}
            return state
      
      def 结构():
            state = {}
            return state
      
      def 用途():
            state = {}
            return state

      def 关系():
            state = {}
            return state

      def 起源():
                 

            state = {}
            return state
      
      def 属性():
               

          state = '由氧和氢组成的无害液体'
          return state
      
      

      def 影响():
            relevance = {}
                 
            return relevance

      def 被影响():
            state = {}
            return state
      
      def 特征():
            state = {}
            return state
      
      def 理由():
            state = {}
            return state
      
      def 位置():
            state = {}
            
            return state
      
      def 变化():
            state = {}
            return state
      
      def 需要():
                 

            state = {}
            
            return state
      def 必需():
                 
            state = {}
            return state
      
      def 方法():

            state = {}
            
            return state
      
      def 过去():
            state = {}
            return state

      def 现在():
            state = {}
            return state

      def 将来():
            state = {}
            return state

      def 种类():
            state = {}
            return state

      def 数量():
            state = {}
            return state

      def 多余():
                 
            state = {}
            return state
      def 好处():
                 
            state = {}
            return state

      def 危害():
                 
            state = {}
            return state

      def 归属():
                 
                   
            state = {}
            return state

      def 权限():
                 
                   
            state = {}
            return state

      def 允许():
                 
                   
            state = {}
            return state

      def 禁止():
                 
                   
            state = {}
            return state

      def 标签():
            label = '水'     
                     
            return label


      def 未知位置():
            state = {}
            return state

      def 确定位置():
            state = {}

            return state

#//////////////////////////////////////////////////////////////////////////////////////////////////
class 食物(object):       
            
      r_parameter = ''
      def __init__(self):
          print('')
          
      def 对象():

          obj = ['人类','你']
            
          return
          
      
      
      def 大纲(self):
            #er =tw
            all_dir = ['描述','行为','状态','结果','结构','用途','影响','特征','被影响'
                       ,'理由','位置','变化','过去','现在','将来','种类','必需','需要'
                       ,'理由','方法','多余','好处','危害','关系','数量'
                       ,'起源','期望','未知位置','确定位置']
            return all_dir
      
      def 描述():
                  
            state = {}
            return state

      def 行为():
            state = {}
            return state
      
      def 状态():
            describe = {}
            return describe
      
      def 结果():
            state = {}
            return state
      
      def 结构():
            state = {}
            return state
      
      def 用途():
            state = {}
            return state

      def 关系():
            state = {}
            return state

      def 起源():
                 

            state = {}
            return state
      
      def 期望():
                 

            state = {}
            return state
      
      

      def 影响():
            relevance = {}
                 
            return relevance

      def 被影响():
            state = {}
            return state
      
      def 特征():
            state = {}
            return state
      
      def 理由():
            state = {}
            return state
      
      def 位置():
            state = {}
            
            return state
      
      def 变化():
            state = {}
            return state
      
      def 需要():
                 

            state = {}
            
            return state
      def 必需():
                 
            state = {}
            return state
      
      def 方法():

            state = {}
            
            return state
      
      def 过去():
            state = {}
            return state

      def 现在():
            state = {}
            return state

      def 将来():
            state = {}
            return state

      def 种类():
            state = {}
            return state

      def 数量():
            state = {}
            return state

      def 多余():
                 
            state = {}
            return state
      def 好处():
                 
            state = {}
            return state

      def 危害():
                 
            state = {}
            return state

      def 归属():
                 
                   
            state = {}
            return state

      def 权限():
                 
                   
            state = {}
            return state

      def 允许():
                 
                   
            state = {}
            return state

      def 禁止():
                 
                   
            state = {}
            return state

      def 标签():
            label = '食物'     
                     
            return label


      def 未知位置():
            state = {}
            return state

      def 确定位置():
            state = {}

            return state
#///////////////////////////////////////////////////////////////////////////////////////////////////

#///////////////////////////////////////////////////////////////////////////////////////////////////
class 空气(object):       
      
      
      r_parameter = ''
      def __init__(self):
          print('')
          
      def 对象():

          obj = ['人类','你']
          return obj
          
      
      
      def 大纲(self):
            #er =tw
            all_dir = ['描述','行为','状态','结果','结构','用途','影响','特征','被影响'
                       ,'理由','位置','变化','过去','现在','将来','种类','必需','需要'
                       ,'理由','方法','多余','好处','危害','关系','数量'
                       ,'起源','期望','未知位置','确定位置']
            return all_dir
      
      def 描述():
                  
            state = {}
            return state

      def 行为():
            state = {}
            return state
      
      def 状态():
            describe = {}
            return describe
      
      def 结果():
            state = {}
            return state
      
      def 结构():
            state = {}
            return state
      
      def 用途():
            state = {}
            return state

      def 关系():
            state = {}
            return state

      def 起源():
                 

            state = {}
            return state
      
      def 期望():
                 

            state = {}
            return state
      
      

      def 影响():
            relevance = {}
                 
            return relevance

      def 被影响():
            state = {}
            return state
      
      def 特征():
            state = {}
            return state
      
      def 理由():
            state = {}
            return state
      
      def 位置():
            state = {}
            
            return state
      
      def 变化():
            state = {}
            return state
      
      def 需要():
                 

            state = {}
            
            return state
      def 必需():
                 
            state = {}
            return state
      
      def 方法():

            state = {}
            
            return state
      
      def 过去():
            state = {}
            return state

      def 现在():
            state = {}
            return state

      def 将来():
            state = {}
            return state

      def 种类():
            state = {}
            return state

      def 数量():
            state = {}
            return state

      def 多余():
                 
            state = {}
            return state
      def 好处():
                 
            state = {}
            return state

      def 危害():
                 
            state = {}
            return state

      def 归属():
                 
                   
            state = {}
            return state

      def 权限():
                 
                   
            state = {}
            return state

      def 允许():
                 
                   
            state = {}
            return state

      def 禁止():
                 
                   
            state = {}
            return state

      def 标签():
            label = '空气'     
                     
            return label


      def 未知位置():
            state = {}
            return state

      def 确定位置():
            state = {}

            return state
      
#///////////////////////////////////////////////////////////////////////////////////////////////////

class 睡眠(object):       
      
      global obj_flag
      global storage_usr_info
      #global current_key_word_obj
      global usr_in_word_len
      global mood
      global reason      
      r_parameter = ''
      def __init__(self):
          print('')
          
      def 对象(self):

          obj = ['人类','你','狗','爸爸','妈妈']
          return obj
          
      def obj():
          global current_key_word_obj
          global obj_flag
          
          print('')
          
          for loc,obj_list in enumerate(mood_obj):
              print(loc,obj_list)
              if conversion_person_key_word == obj_list:
                   obj_flag = True
                   #os.system("pause")
                   break
              else:
                   if n_ksym_kperson == True:
                      obj_flag = True
                   else:
                      obj_flag = False
                                         
          print(obj_flag,conversion_person_key_word)         
          current_key_word_obj = mood_obj#注意
          print(current_key_word_obj)
          #os.system("pause")
          return obj_flag
      
      def 大纲(self):
            #er =tw
            all_dir = ['描述','行为','状态','结果','结构','用途','影响','特征','被影响'
                       ,'理由','位置','变化','过去','现在','将来','种类','必需','需要'
                       ,'理由','方法','多余','好处','危害','关系','数量'
                       ,'起源','期望','未知位置','确定位置']
            return all_dir
      
      def 描述():
                  
            state = {}
            return state

      def 行为():
            state = {}
            return state
      
      def 状态():
            describe = {}
            return describe
      
      def 结果():
            state = {}
            return state
      
      def 结构():
            state = {}
            return state
      
      def 用途():
            state = {}
            return state

      def 关系():
            state = {}
            return state

      def 起源():
                 

            state = {}
            return state
      
      def 期望():
                 

            state = {}
            return state
      
      

      def 影响():
            relevance = {}
                 
            return relevance

      def 被影响():
            state = {}
            return state
      
      def 特征():
            state = {}
            return state
      
      def 理由():
            state = {}
            return state
      
      def 位置():
            state = {}
            
            return state
      
      def 变化():
            state = {}
            return state
      
      def 需要():
                 

            state = {}
            
            return state
      def 必需():
                 
            state = {}
            return state
      
      def 方法():

            state = {}
            
            return state
      
      def 过去():
            state = {}
            return state

      def 现在():
            state = {}
            return state

      def 将来():
            state = {}
            return state

      def 种类():
            state = {}
            return state

      def 数量():
            state = {}
            return state

      def 多余():
                 
            state = {}
            return state
      def 好处():
                 
            state = {}
            return state

      def 危害():
                 
            state = {}
            return state

      def 归属():
                 
                   
            state = {}
            return state

      def 权限():
                 
                   
            state = {}
            return state

      def 允许():
                 
                   
            state = {}
            return state

      def 禁止():
                                    
            state = {}
            return state
      
      def 标签():
            label = '睡眠'
            return label

      def 未知位置():
            state = {}
            return state

      def 确定位置():
            state = {}

            return state
#//////////////////////////////////////////////////////////////////////////////////////////////////
class 太阳(object):       
      
      global obj_flag
      global storage_usr_info
      #global current_key_word_obj
      global usr_in_word_len
      global mood
      global reason      
      r_parameter = ''
      def __init__(self):
          print('')
          
      def 对象(self):
          print('')
          
      def obj():
          global current_key_word_obj
          global obj_flag
          
          print('')
          
          for loc,obj_list in enumerate(mood_obj):
              print(loc,obj_list)
              if conversion_person_key_word == obj_list:
                   obj_flag = True
                   #os.system("pause")
                   break
              else:
                   if n_ksym_kperson == True:
                      obj_flag = True
                   else:
                      obj_flag = False
                                         
          print(obj_flag,conversion_person_key_word)         
          current_key_word_obj = mood_obj#注意
          print(current_key_word_obj)
          #os.system("pause")
          return obj_flag
      
      def 大纲(self):
            #er =tw
            all_dir = ['描述','行为','状态','结果','结构','用途','影响','特征','被影响'
                       ,'理由','位置','变化','过去','现在','将来','种类','必需','需要'
                       ,'理由','方法','多余','好处','危害','关系','数量'
                       ,'起源','期望','未知位置','确定位置']
            return all_dir
      
      def 描述():
                  
            state = {}
            return state

      def 行为():
            state = {}
            return state
      
      def 状态():
            describe = {}
            return describe
      
      def 结果():
            state = {}
            return state
      
      def 结构():
            state = {}
            return state
      
      def 用途():
            state = {}
            return state

      def 关系():
            state = {}
            return state

      def 起源():
                 

            state = {}
            return state
      
      def 期望():
                 

            state = {}
            return state
      
      

      def 影响():
            relevance = {}
                 
            return relevance

      def 被影响():
            state = {}
            return state
      
      def 特征():
            state = {}
            return state
      
      def 理由():
            state = {}
            return state
      
      def 位置():
            state = {'':[''],'':[''],'':['']}
            
            return state
      
      def 变化():
            state = {}
            return state
      
      def 需要():
                 

            state = {}
            
            return state
      def 必需():
                 
            state = {}
            return state
      
      def 方法():

            state = {}
            
            return state
      
      def 过去():
            state = {}
            return state

      def 现在():
            state = {}
            return state

      def 将来():
            state = {}
            return state

      def 种类():
            state = {}
            return state

      def 数量():
            state = {'':''}
            return state

      def 多余():
                 
            state = {}
            return state
      def 好处():
                 
            state = {}
            return state

      def 危害():
                 
            state = {}
            return state

      def 归属():
                 
                   
            state = {}
            return state

      def 权限():
                 
                   
            state = {}
            return state

      def 允许():
                 
                   
            state = {}
            return state

      def 禁止():
                                    
            state = {}
            return state
      
      def 标签():
            label = '实体'
            return label

      def 未知位置():
            state = {}
            return state

      def 确定位置():
            state = {}

            return state      
#//////////////////////////////////////////////////////////////////////////////////////////////////
class 月亮(object):       
      
      global obj_flag
      global storage_usr_info
      #global current_key_word_obj
      global usr_in_word_len
      global mood
      global reason      
      r_parameter = ''
      def __init__(self):
          print('')
          
      def 对象(self):
          print('')
          
      def obj():
          global current_key_word_obj
          global obj_flag
          
          print('')
          
          for loc,obj_list in enumerate(mood_obj):
              print(loc,obj_list)
              if conversion_person_key_word == obj_list:
                   obj_flag = True
                   #os.system("pause")
                   break
              else:
                   if n_ksym_kperson == True:
                      obj_flag = True
                   else:
                      obj_flag = False
                                         
          print(obj_flag,conversion_person_key_word)         
          current_key_word_obj = mood_obj#注意
          print(current_key_word_obj)
          #os.system("pause")
          return obj_flag
      
      def 大纲(self):
            #er =tw
            all_dir = ['描述','行为','状态','结果','结构','用途','影响','特征','被影响'
                       ,'理由','位置','变化','过去','现在','将来','种类','必需','需要'
                       ,'理由','方法','多余','好处','危害','关系','数量'
                       ,'起源','期望','未知位置','确定位置']
            return all_dir
      
      def 描述():
                  
            state = {}
            return state

      def 行为():
            state = {}
            return state
      
      def 状态():
            describe = {}
            return describe
      
      def 结果():
            state = {}
            return state
      
      def 结构():
            state = {}
            return state
      
      def 用途():
            state = {}
            return state

      def 关系():
            state = {}
            return state

      def 起源():
                 

            state = {}
            return state
      
      def 期望():
                 

            state = {}
            return state
      
      

      def 影响():
            relevance = {}
                 
            return relevance

      def 被影响():
            state = {}
            return state
      
      def 特征():
            state = {}
            return state
      
      def 理由():
            state = {}
            return state
      
      def 位置():
            state = {'':[''],'':[''],'':['']}
            
            return state
      
      def 变化():
            state = {}
            return state
      
      def 需要():
                 

            state = {}
            
            return state
      def 必需():
                 
            state = {}
            return state
      
      def 方法():

            state = {}
            
            return state
      
      def 过去():
            state = {}
            return state

      def 现在():
            state = {}
            return state

      def 将来():
            state = {}
            return state

      def 种类():
            state = {}
            return state

      def 数量():
            state = {'':''}
            return state

      def 多余():
                 
            state = {}
            return state
      def 好处():
                 
            state = {}
            return state

      def 危害():
                 
            state = {}
            return state

      def 归属():
                 
                   
            state = {}
            return state

      def 权限():
                 
                   
            state = {}
            return state

      def 允许():
                 
                   
            state = {}
            return state

      def 禁止():
                                    
            state = {}
            return state
      
      def 标签():
            label = '实体'
            return label

      def 未知位置():
            state = {}
            return state

      def 确定位置():
            state = {}

            return state      
#/////////////////////////////////////////////////////////////////////////////////////////////////
class 健康(object):       
      
      global obj_flag
      global storage_usr_info
      #global current_key_word_obj
      global usr_in_word_len
      global mood
      global reason      
      r_parameter = ''
      def __init__(self):
          print('')
          
      def 对象(self):
          obj = ['人类','你']
          return obj
          
      def obj():
          global current_key_word_obj
          global obj_flag
          
          print('')
          
          for loc,obj_list in enumerate(mood_obj):
              print(loc,obj_list)
              if conversion_person_key_word == obj_list:
                   obj_flag = True
                   #os.system("pause")
                   break
              else:
                   if n_ksym_kperson == True:
                      obj_flag = True
                   else:
                      obj_flag = False
                                         
          print(obj_flag,conversion_person_key_word)         
          current_key_word_obj = mood_obj#注意
          print(current_key_word_obj)
          #os.system("pause")
          return obj_flag
      
      def 大纲(self):
            #er =tw
            all_dir = ['描述','行为','状态','结果','结构','用途','影响','特征','被影响'
                       ,'理由','位置','变化','过去','现在','将来','种类','必需','需要'
                       ,'理由','方法','多余','好处','危害','关系','数量'
                       ,'起源','期望','未知位置','确定位置']
            return all_dir
      
      def 描述():
                  
            state = {}
            return state

      def 行为():
            state = {}
            return state
      
      def 状态():
            describe = {}
            return describe
      
      def 结果():
            state = {}
            return state
      
      def 结构():
            state = {}
            return state
      
      def 用途():
            state = {}
            return state

      def 关系():
            state = {}
            return state

      def 起源():
                 

            state = {}
            return state
      
      def 期望():
                 

            state = {}
            return state
      
      

      def 影响():
            relevance = {}
                 
            return relevance

      def 被影响():
            state = {}
            return state
      
      def 特征():
            state = {}
            return state
      
      def 理由():
            state = {}
            return state
      
      def 位置():
            state = {}
            
            return state
      
      def 变化():
            state = {}
            return state
      
      def 需要():
                 

            state = {}
            
            return state
      def 必需():
                 
            state = {}
            return state
      
      def 方法():

            state = {}
            
            return state
      
      def 过去():
            state = {}
            return state

      def 现在():
            state = {}
            return state

      def 将来():
            state = {}
            return state

      def 种类():
            state = {}
            return state

      def 数量():
            state = {}
            return state

      def 多余():
                 
            state = {}
            return state
      def 好处():
                 
            state = {}
            return state

      def 危害():
                 
            state = {}
            return state

      def 归属():
                 
                   
            state = {}
            return state

      def 权限():
                 
                   
            state = {}
            return state

      def 允许():
                 
                   
            state = {}
            return state

      def 禁止():
                                    
            state = {}
            return state
      
      def 标签():
            label = '生命体状态'
            return label

      def 未知位置():
            state = {}
            return state

      def 确定位置():
            state = {}

            return state          
#//////////////////////////////////////////////////////////////////////////////////////////////////
class 身体(object):       
      
      global obj_flag
      global storage_usr_info
      #global current_key_word_obj
      global usr_in_word_len
      global mood
      global reason      
      r_parameter = ''
      def __init__(self):
          print('')
          
      def 对象(self):
          print('')
          
      
      
      def 大纲(self):
            #er =tw
            all_dir = ['描述','行为','状态','结果','结构','用途','影响','特征','被影响'
                       ,'理由','位置','变化','过去','现在','将来','种类','必需','需要'
                       ,'理由','方法','多余','好处','危害','关系','数量'
                       ,'起源','期望','未知位置','确定位置']
            return all_dir

      def 对象():
            obj = []
            return obj
      
      def 描述():
                  
            state = {}
            return state

      def 行为():
            state = {}
            return state
      
      def 状态():
            describe = {}
            return describe
      
      def 结果():
            state = {}
            return state
      
      def 结构():
            state = {}
            return state
      
      def 用途():
            state = {}
            return state

      def 关系():
            state = {}
            return state

      def 起源():
                 

            state = {}
            return state
      
      def 期望():
                 

            state = {}
            return state
      
      

      def 影响():
            relevance = {}
                 
            return relevance

      def 被影响():
            state = {}
            return state
      
      def 特征():
            state = {}
            return state
      
      def 理由():
            state = {}
            return state
      
      def 位置():
            state = {}
            
            return state
      
      def 变化():
            state = {}
            return state
      
      def 需要():
                 

            state = {}
            
            return state
      def 必需():
                 
            state = {}
            return state
      
      def 方法():

            state = {}
            
            return state
      
      def 过去():
            state = {}
            return state

      def 现在():
            state = {}
            return state

      def 将来():
            state = {}
            return state

      def 种类():
            state = {}
            return state

      def 数量():
            state = {}
            return state

      def 多余():
                 
            state = {}
            return state
      def 好处():
                 
            state = {}
            return state

      def 危害():
                 
            state = {}
            return state

      def 归属():
                 
                   
            state = {}
            return state

      def 权限():
                 
                   
            state = {}
            return state

      def 允许():
                 
                   
            state = {}
            return state

      def 禁止():
                                    
            state = {}
            return state
      
      def 标签():
            label = '身体'
            return label

      def 未知位置():
            state = {}
            return state

      def 确定位置():
            state = {}

            return state          
#//////////////////////////////////////////////////////////////////////////////////////////////////      
class 火(object):       
      
      global obj_flag
      global storage_usr_info
      #global current_key_word_obj
      global usr_in_word_len
      global mood
      global reason      
      r_parameter = ''
      def __init__(self):
          print('')
          
      def 对象(self):
          print('')
          
      
      def 大纲(self):
            #er =tw
            all_dir = ['描述','行为','状态','结果','结构','用途','影响','特征','被影响'
                       ,'理由','位置','变化','过去','现在','将来','种类','必需','需要'
                       ,'理由','方法','多余','好处','危害','关系','数量'
                       ,'起源','期望','未知位置','确定位置']
            return all_dir
      
      def 描述():
                  
            state = {'1':''}
            return state

      def 行为():
            state = {'2':''}
            return state
      
      def 状态():
            describe = {'3':''}
            return describe
      
      def 结果():
            state = {'4':''}
            return state
      
      def 结构():
            state = {'5':''}
            return state
      
      def 用途():
            state = {'6':''}
            return state

      def 关系():
            state = {'7':''}
            return state

      def 起源():
                 

            state = {'8':''}
            return state
      
      def 期望():
                 

            state = {'9':''}
            return state
      
      

      def 影响():
            relevance = {'10':''}
                 
            return relevance

      def 被影响():
            state = {'11':''}
            return state
      
      def 特征():
            state = {'12':''}
            return state
      
      def 理由():
            state = {'13':''}
            return state
      
      def 位置():
            state = {}
            
            return state
      
      def 变化():
            
            state = {'14':''}
            return state
      
      def 需要():
                 
            state = {'15':''}
            
            return state
      def 必需():
                 
            state = {'16':''}
            return state
      
      def 方法():

            state = {'17':''}
            
            return state
      
      def 过去():
            state = {'18':''}
            return state

      def 现在():
            state = {'19':''}
            return state

      def 将来():
            state = {'20':''}
            return state

      def 种类():
            state = {'21':''}
            return state

      def 数量():
            state = {}#
            return state

      def 多余():
                 
            state = {'22':''}
            return state
      def 好处():
                 
            state = {'23':''}
            return state

      def 危害():
                 
            state = {'24':''}
            return state

      def 归属():
                 
                   
            state = {'25':''}
            return state

      def 权限():
                 
                   
            state = {'26':''}
            return state

      def 允许():
                 
                   
            state = {'27':''}
            return state

      def 禁止():
                 
                   
            state = {'28':''}
            return state

      def 标签():
            label = '火'
            return label


      def 未知位置():
            state = {'29':''}
            return state

      def 确定位置():
            state = {'30':''}

            return state
#--------------------------------------------------------------------------------------------------
      
#//////////////////////////////////////////////////////////////////////////////////////////////////
class 飞机(object):      
      global obj_flag
      global storage_usr_info
      #global current_key_word_obj
      global usr_in_word_len
      global mood
      global reason      
      r_parameter = ''
      def __init__(self):
          print('')
          
      def 对象(self):
          print('')
          
     
      
      def 大纲(self):
            #er =tw
            all_dir = ['描述','行为','状态','结果','结构','用途','影响','特征','被影响'
                       ,'理由','位置','变化','过去','现在','将来','种类','必需','需要'
                       ,'理由','方法','多余','好处','警告','危害','关系','数量','速度'
                       ,'起源','期望','未知位置','确定位置']
            return all_dir
      
      def 描述():
                  
            state = {}
            return state

      def 行为():
            state = {}
            return state
      
      def 状态():
            describe = {}
            return describe
      
      def 结果():
            state = {}
            return state
      
      def 结构():
            state = {}
            return state
      
      def 用途():
            state = {}
            return state

      def 关系():
            state = {}
            return state

      def 起源():
                 

            state = {}
            return state
      
      def 期望():
                 

            state = {}
            return state
      
      

      def 影响():
            relevance = {}
                 
            return relevance

      def 被影响():
            state = {}
            return state
      
      def 特征():
            state = {}
            return state
      
      def 理由():
            state = {}
            return state
      
      def 位置():
            state = {}
            
            return state
      
      def 变化():
            state = {}
            return state
      
      def 需要():
                 

            state = {}
            
            return state
      def 必需():
                 
            state = {}
            return state
      
      def 方法():

            state = {}
            
            return state
      
      def 过去():
            state = {}
            return state

      def 现在():
            state = {}
            return state

      def 将来():
            state = {}
            return state

      def 种类():
            state = {}
            return state

      def 数量():
            state = {}#
            return state

      def 速度():
            state = {}#
            return state

      def 多余():
                 
            state = {}
            return state
      def 好处():
                 
            state = {}
            return state

      def 危害():
                 
            state = {}
            return state

      def 警告():
                 
            state = {}
            return state

      def 归属():
                 
                   
            state = {}
            return state

      def 权限():
                 
                   
            state = {}
            return state

      def 允许():
                 
                   
            state = {}
            return state

      def 禁止():
                 
                   
            state = {}
            return state


      def 未知位置():
            state = {}
            return state

      def 确定位置():
            state = {}

            return state
#//////////////////////////////////////////////////////////////////////////////////////////////////
class 车(object):      
      global obj_flag
      global storage_usr_info
      #global current_key_word_obj
      global usr_in_word_len
      global mood
      global reason      
      r_parameter = ''
      def __init__(self):
          print('')
          
      def 对象(self):
          print('')
          
      
      
      def 大纲(self):
            #er =tw
            all_dir = ['描述','行为','状态','结果','结构','用途','影响','特征','被影响'
                       ,'理由','位置','变化','过去','现在','将来','种类','必需','需要'
                       ,'理由','方法','多余','好处','警告','危害','关系','数量','速度'
                       ,'起源','期望','未知位置','确定位置']
            return all_dir
      
      def 描述():
                  
            state = {}
            return state

      def 行为():
            state = {}
            return state
      
      def 状态():
            describe = {}
            return describe
      
      def 结果():
            state = {}
            return state
      
      def 结构():
            state = {}
            return state
      
      def 用途():
            state = {}
            return state

      def 关系():
            state = {}
            return state

      def 起源():
                 

            state = {}
            return state
      
      def 期望():
                 

            state = {}
            return state
      
      

      def 影响():
            relevance = {}
                 
            return relevance

      def 被影响():
            state = {}
            return state
      
      def 特征():
            state = {}
            return state
      
      def 理由():
            state = {}
            return state
      
      def 位置():
            state = {}
            
            return state
      
      def 变化():
            state = {}
            return state
      
      def 需要():
                 

            state = {}
            
            return state
      def 必需():
                 
            state = {}
            return state
      
      def 方法():

            state = {}
            
            return state
      
      def 过去():
            state = {}
            return state

      def 现在():
            state = {}
            return state

      def 将来():
            state = {}
            return state

      def 种类():
            state = {}
            return state

      def 数量():
            state = {}#
            return state

      def 速度():
            state = {}#
            return state

      def 多余():
                 
            state = {}
            return state
      def 好处():
                 
            state = {}
            return state

      def 危害():
                 
            state = {}
            return state

      def 警告():
                 
            state = {}
            return state

      def 归属():
                 
                   
            state = {}
            return state

      def 权限():
                 
                   
            state = {}
            return state

      def 允许():
                 
                   
            state = {}
            return state

      def 禁止():
                 
                   
            state = {}
            return state


      def 未知位置():
            state = {}
            return state

      def 确定位置():
            state = {}

            return state

      def 标签(self):
          obj = '交通工具'
          return obj
#//////////////////////////////////////////////////////////////////////////////////////////////////
class 船(object):      
      global obj_flag
      global storage_usr_info
      #global current_key_word_obj
      global usr_in_word_len
      global mood
      global reason      
      r_parameter = ''
      def __init__(self):
          print('')
          
      def 对象(self):
          print('')
          
      
      
      def 大纲(self):
            #er =tw
            all_dir = ['描述','行为','状态','结果','结构','用途','影响','特征','被影响'
                       ,'理由','位置','变化','过去','现在','将来','种类','必需','需要'
                       ,'理由','方法','多余','好处','警告','危害','关系','数量','速度'
                       ,'起源','期望','未知位置','确定位置']
            return all_dir
      
      def 描述():
                  
            state = {}
            return state

      def 行为():
            state = {}
            return state
      
      def 状态():
            describe = {}
            return describe
      
      def 结果():
            state = {}
            return state
      
      def 结构():
            state = {}
            return state
      
      def 用途():
            state = {}
            return state

      def 关系():
            state = {}
            return state

      def 起源():
                 

            state = {}
            return state
      
      def 期望():
                 

            state = {}
            return state
      
      

      def 影响():
            relevance = {}
                 
            return relevance

      def 被影响():
            state = {}
            return state
      
      def 特征():
            state = {}
            return state
      
      def 理由():
            state = {}
            return state
      
      def 位置():
            state = {}
            
            return state
      
      def 变化():
            state = {}
            return state
      
      def 需要():
                 

            state = {}
            
            return state
      def 必需():
                 
            state = {}
            return state
      
      def 方法():

            state = {}
            
            return state
      
      def 过去():
            state = {}
            return state

      def 现在():
            state = {}
            return state

      def 将来():
            state = {}
            return state

      def 种类():
            state = {}
            return state

      def 数量():
            state = {}#
            return state

      def 速度():
            state = {}#
            return state

      def 多余():
                 
            state = {}
            return state
      def 好处():
                 
            state = {}
            return state

      def 危害():
                 
            state = {}
            return state

      def 警告():
                 
            state = {}
            return state

      def 归属():
                 
                   
            state = {}
            return state

      def 权限():
                 
                   
            state = {}
            return state

      def 允许():
                 
                   
            state = {}
            return state

      def 禁止():
                 
                   
            state = {}
            return state

      
      def 标签():
                 
          label = '实体'
          return label

      def 未知位置():
            state = {}
            return state

      def 确定位置():
            state = {}

            return state
#//////////////////////////////////////////////////////////////////////////////////////////////////
class 东西(object):
      
           
      global obj_flag
      global storage_usr_info
      #global current_key_word_obj
      global usr_in_word_len
      global mood
      global reason
      
      r_parameter = ''

      def __init__(self):
          print('')
          
      def 对象(self):
          print('')
          
      
      
      def 大纲(self):
            #er =tw
            all_dir = ['描述','行为','状态','结果','结构','用途','影响','特征','被影响'
                       ,'理由','位置','变化','过去','现在','将来','种类','必需','需要'
                       ,'理由','方法','多余','好处','危害','关系','数量'
                       ,'起源','期望','未知位置','确定位置']
            return all_dir
      
      def 描述():
                  
            state = {}
            return state

      def 行为():
            state = {}
            return state
      
      def 状态():
            describe = {}
            return describe
      
      def 结果():
            state = {}
            return state
      
      def 结构():
            state = {}
            return state
      
      def 用途():
            state = {}
            return state

      def 关系():
            state = {}
            return state

      def 起源():
                 

            state = {}
            return state
      
      def 期望():
                 

            state = {}
            return state
      
      

      def 影响():
            relevance = {}
                 
            return relevance

      def 被影响():
            state = {}
            return state
      
      def 特征():
            state = {}
            return state
      
      def 理由():
            state = {}
            return state
      def 位置():
            state = {}
            return state
      
      def 变化():
            state = {}
            return state
      
      def 需要():
                 

            state = {}
            
            return state
      
      def 必需():
                 
            state = {}
            return state
      
      def 方法():

            state = {}
            
            return state
      
      def 过去():
            state = {}
            return state

      def 现在():
            state = {}
            return state

      def 将来():
            state = {}
            return state

      def 种类():
            state = {}
            return state

      def 数量():
            state = {}
            return state

      def 多余():
                 
            state = {}
            return state
      def 好处():
                 
            state = {}
            return state

      def 危害():
                 
            state = {}
            return state

      def 归属():
                 
                   
            state = {}
            return state

      def 权限():
                                   
            state = {}
            return state

      def 允许():
                 
                   
            state = {}
            return state

      def 禁止():
                 
                   
            state = {}
            return state

      def 赞扬():                 
                   
            state = {}
            return state


      def 未知位置():
            state = {}
            return state

      def 确定位置():
            state = {}
            return state
#//////////////////////////////////////////////////////////////////////////////////////////////////

#//////////////////////////////////////////////////////////////////////////////////////////////////
class 胃口(object):
      


      def __init__(self):
          print('')
          
      def 对象(self):
          print('')
          
      
      def 属性(self):
            r_parameter = ''
            return r_parameter

      
      def 标签(self):
          label = ''
          return label      
      
#//////////////////////////////////////////////////////////////////////////////////////////////////
class 心情(object):
      
      def __init__(self):
          print('')
          
      def 对象(self):

          obj = ['人类','你','狗','爸爸','妈妈']
          return obj
          
          
      def 属性(self):
            r_parameter = ''
            return r_parameter

      
      def 标签():
          label = '情绪'
          return label
           
#//////////////////////////////////////////////////////////////////////////////////////////////////
class 说(object):
      

      def __init__(self):
          print('')
          
      def 对象(self):

          obj = ['我','你','人类','爸爸','妈妈']
          return obj
          
          
      def 属性(self):
            r_parameter = ''
            return r_parameter

      
      def 标签():
          label = '行为'
          return label
#//////////////////////////////////////////////////////////////////////////////////////////////////
class 给(object):
      

      def __init__(self):
          print('')
          
      def 对象(self):

          obj = ['我','你','人类','爸爸','妈妈']
          return obj
          
          
      def 属性(self):
            r_parameter = ''
            return r_parameter

      
      def 标签():
          label = '指向对象'
          return label     
#//////////////////////////////////////////////////////////////////////////////////////////////////
class 不好(object):

      def 属性(self):
            r_parameter = ''
            return r_parameter

      def 标签(self):
          label = '不好'
          return label
#//////////////////////////////////////////////////////////////////////////////////////////////////
class 思念(object):      
     
          
      def 对象(self):
          print('')

      
      def 属性(self):
            r_parameter = ''
            return r_parameter

      def 标签(self):
          label = '情绪'
          return label

#//////////////////////////////////////////////////////////////////////////////////////////////////
class 想(object):

          
      def 对象(self):
          print('')
          
      
      
      def 属性(self):
            r_parameter = ''
            return r_parameter

      def 多义(self):
            state = ''
           
            return state

#//////////////////////////////////////////////////////////////////////////////////////////////////
      
#//////////////////////////////////////////////////////////////////////////////////////////////////
class 协助(object):
      global obj_flag
      global storage_usr_info
      #global current_key_word_obj
      global usr_in_word_len
      r_parameter = ''
      def __init__(self):
          print('')
          
      def 对象(self):
          print('')
          
      
      
      def 属性(self):
            r_parameter = ''
            return r_parameter
      def 状态(self):
            state = {''}

            return state
      
      def 多义(self):
            state = ''
            
            return state
      
      def 特性(self):
            global reason
            reason = 2
            return reason
      def 判断(self):
            ambiguity = True
            return ambiguity
          
#//////////////////////////////////////////////////////////////////////////////////////////////////
class 开心(object):
      global obj_flag
      global storage_usr_info
      #global current_key_word_obj
      global usr_in_word_len
      r_parameter = ''

      def __init__(self):
          print('')
          
      def 对象(self):

          obj = ['人类','你','狗','爸爸','妈妈']
          return obj
                    
      
      def 属性(self):
            r_parameter = ''
            return r_parameter
      

      def 标签():
            
            label = '情绪'            
            return label
            
#///////////////////////////////////////////////////////////////////////////////////////////////////
class 会(object):
      global obj_flag
      global storage_usr_info
      #global current_key_word_obj
      global usr_in_word_len
      r_parameter = ''

      def __init__(self):
          print('')
          
      def 对象(self):

          obj = ['人类','你','狗','爸爸','妈妈']
          return obj
                    
      
      def 属性(self):
            r_parameter = ''
            return r_parameter
      

      def 标签():
            
            label = '意向'            
            return label

#//////////////////////////////////////////////////////////////////////////////////////////////////
class 笑(object):
      global obj_flag
      global storage_usr_info
      #global current_key_word_obj
      global usr_in_word_len
      r_parameter = ''

      def __init__(self):
          print('')
          
      def 对象(self):

          obj = ['人类','你','狗','爸爸','妈妈']
          return obj
                    
      
      def 属性(self):
            r_parameter = ''
            return r_parameter
      

      def 标签():
            
            label = '行为'            
            return label
            
#///////////////////////////////////////////////////////////////////////////////////////////////////

class 难过(object):
      global obj_flag
      global storage_usr_info
      #global current_key_word_obj
      global usr_in_word_len
      r_parameter = ''

      def __init__(self):
          print('')
          
      def 对象(self):

          obj = ['人类','你','狗','爸爸','妈妈']
          return obj
                    
      
      def 属性(self):
            r_parameter = ''
            return r_parameter
      

      def 标签():
            
            label = '情绪'            
            return label
            
#///////////////////////////////////////////////////////////////////////////////////////////////////
class 考试(object):
      global obj_flag
      global storage_usr_info
      #global current_key_word_obj
      global usr_in_word_len
      global exam
      #global reason
      
      r_parameter = ''

      def __init__(self):
          print('')
          
      def 对象(self):
          print('')
          
      
      
      def 探测(self):
            c_name = ''
            return c_name
      
      def 属性(self):
            r_parameter = ''
            return r_parameter
      def 状态(self):
            state = {}

            return state
      def 查询(self):
            check = {}
            return check
      
      def 特性(self):
            relevance = []
            
            global reason
            if reason == 0:
               exam = 1
               reason = 1               
            elif reason == 1:
                 exam = 2
                 reason = 2
            elif reason == 2:
                 exam = 3
                 reason = 3
                 
            return reason,relevance
#//////////////////////////////////////////////////////////////////////////////////////////////////
class 人类(object):
      global obj_flag
      global storage_usr_info
      #global current_key_word_obj
      global usr_in_word_len
      global mood
      global reason      
      method_state = []
      result_state = []
      hight_state = []
      weight_state = []
      emotion_state = []
      forbid_state = []
      harm_state = []
      need_state = []
      conseq_state = []
      result = ''
      
      def __init__(self):
          print('')
          

      
      def 大纲(self):
            #er =tw
            all_dir = ['描述','行为','状态','结果','结构','身高','体重','用途','影响'
                       ,'特征','被影响','位置','变化','过去','现在','将来','种类'
                       ,'必需','需要','内容','条件','理由','原因','方法','多余'
                       ,'好处','危害','关系','数量','情绪','伴侣','结果','后果'
                       ,'起源','期望','日常','禁止','未知位置','确定位置']
            return all_dir

      def 对象():
          obj = []
          return obj
      
      def 描述():
                  
            state = {}
            return state

      def 行为():
            state = {}
            return state
      
      def 状态():
            describe = {}
            return describe
      
      def 条件(self,multiple):

            state = []
            parameter = multiple
            t_judge = False
            global find_answer_flag
            
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               pass
            
            else:
               state.append(parameter)
               print('㊣㊣㊣㊣学习完成♠♠♠♠子项--条件',state)
               #os.system("pause")                
      

      
      def 结构():
            state = {}
            return state

      def 身高(self,multiple):
            
            global find_answer_flag      
            parameter = multiple
            t_judge = False
            result_flag = False
                                    
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
                     
               current_list = self.hight_state   
               print('看看--->>>',parameter)
               print('关键☛☛☛☛', current_list,self.hight_state)
               
               for clc,clk in enumerate(current_list):
                   for cdc,cdk in clk.items():
                       if parameter == cdc:
                          self.result = cdk                          
                          find_answer_flag = True
                          print('返回答案--键:',cdk)
                          return self.result
                          
                       elif parameter == cdk:
                          self.result = cdc
                          find_answer_flag = True
                          print('返回答案--值:',cdc)
                          return self.result
                          
                          
                       elif parameter in cdc:
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--相似键:',cdc)
                          return self.result

                       elif parameter in cdk:
                          self.result =  cdc + cdk
                          find_answer_flag = True
                          print('返回答案--相似值:',cdk)
                          return self.result

                       elif cdc in parameter:
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--键相似:',cdc)
                          return self.result

                       elif cdk in parameter :
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--值相似:',cdk)
                          return self.result

               if find_answer_flag == False:
                  result_flag = False
                  
                  return result_flag
               #os.system("pause")   
               
               #return result
            
            else:
               #state.append(parameter)
               self.hight_state.append(parameter)
               print('㊣㊣㊣㊣学习完成','♠♠♠♠子项:身高',self.hight_state)
               #os.system("pause")

      def 体重(self,multiple):
            global find_answer_flag      
            parameter = multiple
            t_judge = False
                                    
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               current_list = self.weight_state   
               print('看看--->>>',parameter)
               print('关键☛☛☛☛', current_list,self.weight_state)
               
               for clc,clk in enumerate(current_list):
                   for cdc,cdk in clk.items():
                       if parameter == cdc:
                          self.result = cdk                          
                          find_answer_flag = True
                          print('返回答案--键:',cdk)
                          return self.result
                          
                       elif parameter == cdk:
                          self.result = cdc
                          find_answer_flag = True
                          print('返回答案--值:',cdc)
                          return self.result
                          
                          
                       elif parameter in cdc:
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--相似键:',cdc)
                          return self.result

                       elif parameter in cdk:
                          self.result =  cdc + cdk
                          find_answer_flag = True
                          print('返回答案--相似值:',cdk)
                          return self.result

                       elif cdc in parameter:
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--键相似:',cdc)
                          return self.result

                       elif cdk in parameter :
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--值相似:',cdk)
                          return self.result

                          
               #os.system("pause")
               
               return result#self.method_state#study_count
            
            else:
               #state.append(parameter)
               self.highe_state.append(parameter)
               print('㊣㊣㊣㊣学习完成','♠♠♠♠子项:体重',self.weight_state)
               #os.system("pause")
      
      def 用途():
            state = {}
            return state

      def 关系():
            state = {}
            return state

      def 起源():
                 
            state = {}
            return state
      
      def 期望():
                 
            state = {}
            return state

      

      def 影响():
            relevance = {}
                 
            return relevance

      def 被影响():
            state = {}
            return state
      
      def 特征():
            state = {}
            return state
      
      def 理由(self,multiple):
            state = []
            parameter = multiple
            t_judge = False
            global find_answer_flag
            
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               current_list = self.method_state   
               print('看看--->>>',parameter)
               print('关键☛☛☛☛', current_list,self.method_state)
               
               for clc,clk in enumerate(current_list):
                   for cdc,cdk in clk.items():
                       if parameter == cdc:
                          result = cdk
                          find_answer_flag = True
                          print('返回答案--键:',cdk)
                          
                       elif parameter == cdk:
                          result = cdc
                          find_answer_flag = True
                          print('返回答案--值:',cdc)
                          
                       elif parameter in cdc:
                          result = cdk   
                          print('返回答案--相似键:',cdk)

                       elif parameter in cdk:
                          result = cdc
                          find_answer_flag = True
                          print('返回答案--相似值:',cdc)

                       elif cdc in parameter:
                          result = cdk
                          find_answer_flag = True
                          print('返回答案--键相似:',cdk)

                       elif cdk in parameter :
                          result = cdc
                          find_answer_flag = True
                          print('返回答案--值相似:',cdc)

                       elif difflib.SequenceMatcher(None, cdc,parameter).ratio() >= sim_ref_value:
                            result = cdk
                            find_answer_flag = True
                            print('返回答案--值相似:',cdc)

                       elif difflib.SequenceMatcher(None, cdk,parameter).ratio() >= sim_ref_value:
                            result = cdc
                            find_answer_flag = True
                            print('返回答案--值相似:',cdc)     
                          

               print('☛☛☛☛看相似度:')
                     #,sim_sub_list)
               #result = sim_sub_list[sim_loc]
               return result#self.method_state#study_count
            
            else:
               state.append(parameter)
               print('㊣㊣㊣㊣学习完成',state)
               #os.system("pause")

      def 原因(self,multiple):
            state = []
            parameter = multiple
            t_judge = False
            global find_answer_flag
            
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               pass
            
            else:
               state.append(parameter)
               print('㊣㊣㊣㊣学习完成',state)
               #os.system("pause")
      
      def 位置():
            state = {}
            
            return state
      
      def 变化():
            state = {}
            return state
      
      def 需要(self,multiple):
            
          global find_answer_flag
          global force_out_ansewr
          parameter = multiple
          t_judge = False
          result = ''
          sim_ref_value = 0.4
            
          t_judge = isinstance(parameter, str)#判断属于字符或字典
            
          if t_judge:
               current_list = self.need_state   
               print('看看--->>>',parameter)
               print('关键☛☛☛☛', current_list,self.need_state)
               
               for clc,clk in enumerate(current_list):
                   for cdc,cdk in clk.items():
                       if parameter == cdc:
                          self.result = cdk                          
                          find_answer_flag = True
                          print('返回答案--键:',cdk)
                          #return self.result
                          
                       elif parameter == cdk:
                          self.result = cdc
                          find_answer_flag = True
                          print('返回答案--值:',cdc)
                          #return self.result
                          
                          
                       elif parameter in cdc:
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--相似键:',cdc)
                          #return self.result

                       elif parameter in cdk:
                          self.result =  cdc + cdk
                          find_answer_flag = True
                          print('返回答案--相似值:',cdk)
                          #return self.result

                       elif cdc in parameter:
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--键相似:',cdc)
                          #return self.result

                       elif cdk in parameter :
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--值相似:',cdk)
                          

                       elif difflib.SequenceMatcher(None, cdc,parameter).ratio() >= sim_ref_value:
                            self.result = cdc
                            find_answer_flag = True
                            print('返回答案--值相似:',cdk)

                       elif difflib.SequenceMatcher(None, cdk,parameter).ratio() >= sim_ref_value:
                            self.result = cdk
                            find_answer_flag = True
                            print('返回答案--值相似:',cdk) 

                          
               #os.system("pause")
               if find_answer_flag:
                  return self.result
            
               else:
                     
                  if force_out_ansewr:
                     #print('❉❉❉❉返回原始字典', self.need_state)  
                     return self.need_state
                  
                  else:
            
                      return find_answer_flag#self.method_state#study_count
            
          else:
               #state.append(parameter)
               self.need_state.append(parameter)
               print('㊣㊣㊣㊣学习完成','♠♠♠♠子项:需要',self.need_state)
               #os.system("pause")


      def 结果(self,multiple):
            
          global find_answer_flag
          global force_out_ansewr
          parameter = multiple
          t_judge = False
          result = ''
          sim_ref_value = 0.4
            
          t_judge = isinstance(parameter, str)#判断属于字符或字典
            
          if t_judge:
               current_list = self.result_state   
               print('看看--->>>',parameter)
               print('关键☛☛☛☛', current_list,self.result_state)
               
               for clc,clk in enumerate(current_list):
                   for cdc,cdk in clk.items():
                       if parameter == cdc:
                          self.result = cdk                          
                          find_answer_flag = True
                          print('返回答案--键:',cdk)
                          #return self.result
                          
                       elif parameter == cdk:
                          self.result = cdc
                          find_answer_flag = True
                          print('返回答案--值:',cdc)
                          #return self.result
                          
                          
                       elif parameter in cdc:
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--相似键:',cdc)
                          #return self.result

                       elif parameter in cdk:
                          self.result =  cdc + cdk
                          find_answer_flag = True
                          print('返回答案--相似值:',cdk)
                          #return self.result

                       elif cdc in parameter:
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--键相似:',cdc)
                          #return self.result

                       elif cdk in parameter :
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--值相似:',cdk)
                          

                       elif difflib.SequenceMatcher(None, cdc,parameter).ratio() >= sim_ref_value:
                            self.result = cdk
                            find_answer_flag = True
                            print('返回答案--模糊值相似:',cdk)

                       elif difflib.SequenceMatcher(None, cdk,parameter).ratio() >= sim_ref_value:
                            self.result = cdc
                            find_answer_flag = True
                            print('返回答案--模糊键相似:',cdc) 

                          
               #os.system("pause")
               if find_answer_flag:
                  return self.result
            
               else:
                     
                  if force_out_ansewr:
                     return self.result_state
                  
                  else:
            
                      return find_answer_flag#self.method_state#study_count
            
          else:
               #state.append(parameter)
               self.result_state.append(parameter)
               print('㊣㊣㊣㊣学习完成','♠♠♠♠子项:结果',self.result_state)
               #os.system("pause")

               

      def 后果(self,multiple):
            
          global find_answer_flag
          global force_out_ansewr
          parameter = multiple
          t_judge = False
          result = ''
          sim_ref_value = 0.4
            
          t_judge = isinstance(parameter, str)#判断属于字符或字典
            
          if t_judge:
               current_list = self.conseq_state   
               print('看看--->>>',parameter)
               print('关键☛☛☛☛', current_list,self.conseq_state)
               
               for clc,clk in enumerate(current_list):
                   for cdc,cdk in clk.items():
                       if parameter == cdc:
                          self.result = cdk                          
                          find_answer_flag = True
                          print('返回答案--键:',cdk)
                          #return self.result
                          
                       elif parameter == cdk:
                          self.result = cdc
                          find_answer_flag = True
                          print('返回答案--值:',cdc)
                          #return self.result
                          
                          
                       elif parameter in cdc:
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--相似键:',cdc)
                          #return self.result

                       elif parameter in cdk:
                          self.result =  cdc + cdk
                          find_answer_flag = True
                          print('返回答案--相似值:',cdk)
                          #return self.result

                       elif cdc in parameter:
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--键相似:',cdc)
                          #return self.result

                       elif cdk in parameter :
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--值相似:',cdk)
                          

                       elif difflib.SequenceMatcher(None, cdc,parameter).ratio() >= sim_ref_value:
                            self.result = cdk
                            find_answer_flag = True
                            print('返回答案--模糊值相似:',cdk)

                       elif difflib.SequenceMatcher(None, cdk,parameter).ratio() >= sim_ref_value:
                            self.result = cdc
                            find_answer_flag = True
                            print('返回答案--模糊键相似:',cdc) 

                          
               #os.system("pause")
               if find_answer_flag:
                  return self.result
            
               else:
                     
                  if force_out_ansewr:
                     return self.conseq_state
                  
                  else:
            
                      return find_answer_flag#self.method_state#study_count
            
          else:
               #state.append(parameter)
               self.conseq_state.append(parameter)
               print('㊣㊣㊣㊣学习完成','♠♠♠♠子项:后果',self.conseq_state)
               #os.system("pause")         
      
      def 必需():
                 
            state = {}
            return state
      
      def 方法(self,multiple):
            
            global study_count
            global find_answer_flag

            sim_ref_value = 0.4
            parameter = multiple
            t_judge = False
            result = ''
            
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               current_list = self.method_state   
               print('看看--->>>',parameter)
               print('关键☛☛☛☛', current_list,self.method_state)
               
               for clc,clk in enumerate(current_list):
                   for cdc,cdk in clk.items():
                       if parameter == cdc:
                          result = cdk
                          find_answer_flag = True
                          print('返回答案--键:',cdk)
                          
                       elif parameter == cdk:
                          result = cdc
                          find_answer_flag = True
                          print('返回答案--值:',cdc)
                          
                       elif parameter in cdc:
                          result = cdk   
                          print('返回答案--相似键:',cdk)

                       elif parameter in cdk:
                          result = cdc
                          find_answer_flag = True
                          print('返回答案--相似值:',cdc)

                       elif cdc in parameter:
                          result = cdk
                          find_answer_flag = True
                          print('返回答案--键相似:',cdk)

                       elif cdk in parameter :
                          result = cdc
                          find_answer_flag = True
                          print('返回答案--值相似:',cdc)

                       elif difflib.SequenceMatcher(None, cdc,parameter).ratio() >= sim_ref_value:
                            result = cdk
                            find_answer_flag = True
                            print('返回答案--值相似:',cdc)

                       elif difflib.SequenceMatcher(None, cdk,parameter).ratio() >= sim_ref_value:
                            result = cdc
                            find_answer_flag = True
                            print('返回答案--值相似:',cdc)     
                          
               
               #print('☛☛☛☛看相似度:')
                     #,sim_sub_list)
               #result = sim_sub_list[sim_loc]
               return result#self.method_state#study_count

            
            else:
               study_count.append(parameter)
               self.method_state.append(parameter)
               #current_list = self.method_state
               print('㊣㊣㊣㊣学习完成','♠♠♠♠对应子项:方法',study_count,self.method_state)
               #study_count = state
               #os.system("pause")
               

      def 内容(self,multiple):

            state = []
            parameter = multiple
            t_judge = False
            
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               pass
            
            else:
               state.append(parameter)
               print('㊣㊣㊣㊣学习完成',state)
               #os.system("pause")
      
      def 过去():
            state = {}
            return state

      def 现在():
            state = {}
            return state

      def 将来():
            state = {}
            return state

      def 种类():
            state = {}
            return state

      def 数量(self,multiple):
            state = []
            return state

      def 情绪(self,multiple):
            
            global find_answer_flag      
            parameter = multiple
            t_judge = False
            #result = ''
            sim_ref_value = 0.6
            
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               current_list = self.emotion_state   
               print('看看--->>>',parameter)
               print('关键☛☛☛☛', current_list,self.emotion_state)
               
               for clc,clk in enumerate(current_list):
                   for cdc,cdk in clk.items():
                       if parameter == cdc:
                          self.result = cdk                          
                          find_answer_flag = True
                          print('返回答案--键:',cdk)
                          return self.result
                          
                       elif parameter == cdk:
                          self.result = cdc
                          find_answer_flag = True
                          print('返回答案--值:',cdc)
                          return self.result
                          
                          
                       

                       elif difflib.SequenceMatcher(None, cdc,parameter).ratio() >= sim_ref_value:
                            self.result = cdk
                            find_answer_flag = True
                            print('返回答案--值模糊相似:',cdk)
                            return self.result

                       elif difflib.SequenceMatcher(None, cdk,parameter).ratio() >= sim_ref_value:
                            self.result = cdc
                            find_answer_flag = True
                            print('返回答案--值模糊相似:',cdc)
                            return self.result

                          
               #os.system("pause")
               if find_answer_flag == False:
                     
                  return find_answer_flag#self.method_state#study_count
            
            else:
               #state.append(parameter)
               self.emotion_state.append(parameter)
               print('㊣㊣㊣㊣学习完成','♠♠♠♠子项:情绪',self.emotion_state)
               #os.system("pause")

      def 多余():
                 
            state = {}
            return state
      def 好处():
                 
            state = {}
            return state

      def 危害(self,multiple):
                 
          sim_ref_value = 0.4
          parameter = multiple
          t_judge = False
          result = ''
          global find_answer_flag
            
          t_judge = isinstance(parameter, str)#判断属于字符或字典
            
          if t_judge:
               current_list = self.harm_state   
               print('看看--->>>',parameter)
               print('关键☛☛☛☛', current_list,self.harm_state)
               
               for clc,clk in enumerate(current_list):
                   for cdc,cdk in clk.items():
                       if parameter == cdc:
                          result = cdk
                          find_answer_flag = True
                          print('返回答案--键:',cdk)
                          
                       elif parameter == cdk:
                          result = cdc
                          find_answer_flag = True
                          print('返回答案--值:',cdc)
                          
                       elif parameter in cdc:
                          result = cdk   
                          print('返回答案--相似键:',cdk)

                       elif parameter in cdk:
                          result = cdc
                          find_answer_flag = True
                          print('返回答案--相似值:',cdc)

                       elif cdc in parameter:
                          result = cdk
                          find_answer_flag = True
                          print('返回答案--键相似:',cdk)

                       elif cdk in parameter :
                          result = cdc
                          find_answer_flag = True
                          print('返回答案--值相似:',cdc)

                       elif difflib.SequenceMatcher(None, cdc,parameter).ratio() >= sim_ref_value:
                            result = cdk
                            find_answer_flag = True
                            print('返回答案--值相似:',cdc)

                       elif difflib.SequenceMatcher(None, cdk,parameter).ratio() >= sim_ref_value:
                            result = cdc
                            find_answer_flag = True
                            print('返回答案--值相似:',cdc)
                            
                       else:
                            print('✘✘✘✘解析答案失败')

               print('☛☛☛☛看相似度:')
                     #,sim_sub_list)
               #result = sim_sub_list[sim_loc]
               return result#self.method_state#study_count
            
          else:
               #state.append(parameter)
               self.harm_state.append(parameter)
               print('㊣㊣㊣㊣学习完成,子项-禁止♠♠♠♠',self.harm_state)
               #os.system("pause")

      def 归属():
                 
                   
            state = {}
            return state

      def 权限():
                 
                   
            state = {}
            return state

      def 允许():
                 
                   
            state = {}
            return state

      def 禁止(self,multiple):
          sim_ref_value = 0.4
          parameter = multiple
          t_judge = False
          result = ''
          global find_answer_flag
            
          t_judge = isinstance(parameter, str)#判断属于字符或字典
            
          if t_judge:
               current_list = self.forbid_state   
               print('看看--->>>',parameter)
               print('关键☛☛☛☛', current_list,self.forbid_state)
               
               for clc,clk in enumerate(current_list):
                   for cdc,cdk in clk.items():
                       if parameter == cdc:
                          result = cdk
                          find_answer_flag = True
                          print('返回答案--键:',cdk)
                          
                       elif parameter == cdk:
                          result = cdc
                          find_answer_flag = True
                          print('返回答案--值:',cdc)
                          
                       elif parameter in cdc:
                          result = cdk   
                          print('返回答案--相似键:',cdk)

                       elif parameter in cdk:
                          result = cdc
                          find_answer_flag = True
                          print('返回答案--相似值:',cdc)

                       elif cdc in parameter:
                          result = cdk
                          find_answer_flag = True
                          print('返回答案--键相似:',cdk)

                       elif cdk in parameter :
                          result = cdc
                          find_answer_flag = True
                          print('返回答案--值相似:',cdc)

                       elif difflib.SequenceMatcher(None, cdc,parameter).ratio() >= sim_ref_value:
                            result = cdk
                            find_answer_flag = True
                            print('返回答案--值相似:',cdc)

                       elif difflib.SequenceMatcher(None, cdk,parameter).ratio() >= sim_ref_value:
                            result = cdc
                            find_answer_flag = True
                            print('返回答案--值相似:',cdc)
                            
                       else:
                            print('✘✘✘✘解析答案失败')

               print('☛☛☛☛看相似度:')
                     #,sim_sub_list)
               #result = sim_sub_list[sim_loc]
               return result#self.method_state#study_count
            
          else:
               #state.append(parameter)
               self.forbid_state.append(parameter)
               print('㊣㊣㊣㊣学习完成,子项-禁止♠♠♠♠',self.forbid_state)
               #os.system("pause")

      def 标签():
            label = '人类'
            return label
      
      def 日常():
                         
            state = {}
            return state

      def 对象():
            obj = ['人类','你']
            return obj

      def 未知位置():
            state = {}
            return state

      def 确定位置():
            state = {}

            return state
#/////////////////////////////////////////////////////////////////////////////////////////////////

#/////////////////////////////////////////////////////////////////////////////////////////////////
class  比(object):
      global d_person_match
      global answer_t_list
      global successful
      global cause
      #global have_obj   
      #os.system("pause")
      def __init__(self):
          print("")#第一人称

      global obj_flag
      global storage_usr_info
      #global current_key_word_obj
      global usr_in_word_len
      global mood
      global reason      
      method_state = []
      result_state = []
      call_state   = []
      cmp_state = []
      result = ''
      key = ''
      value = ''
      type_c = False
      d_dict = {}
      
      def __init__(self):
          print('')

      def 对比(self,multiple):
            
            global find_answer_flag      
            parameter = multiple
            t_judge = False
            result = ''
            sim_ref_value = 0.4
                  
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               current_list = self.cmp_state   
               print('看看--->>>',parameter)
               print('关键☛☛☛☛', current_list,self.cmp_state)
               
               for clc,clk in enumerate(current_list):
                   for cdc,cdk in clk.items():
                       if parameter == cdc:
                          self.result = cdc                          
                          find_answer_flag = True
                          print('返回答案--键:',cdc)
                          return self.result
                          
                       elif parameter == cdk:
                          self.result = cdk
                          find_answer_flag = True
                          print('返回答案--值:',cdk)
                          return self.result
                          
                          
                        

                          
               #os.system("pause")
               
               #return result#self.method_state#study_count
            
            else:
               #state.append(parameter)
               self.cmp_state.append(parameter)
               print('㊣㊣㊣㊣学习完成','♠♠♠♠子项:对比',self.cmp_state)
               #os.system("pause")

               #os.system("pause")                         

      def 标签():
          label = '对比行为'
          return label    
#//////////////////////////////////////////////////////////////////////////////////////////////////
class  我(object):
      global d_person_match
      global answer_t_list
      global successful
      global cause

      def __init__(self):
          print("")

      global obj_flag
      global storage_usr_info

      global usr_in_word_len
      global mood
      global reason      
      method_state = []
      result_state = []
      call_state   = []
      attribute_state = []
      source_state = []
      gender_state = []
      location_state = []
      hight_state = []
      weight_state = []
      use_state = []
      cause_state = []
      target_state  = []
      skill_state = []
      action_state = []
      preset_state = []
      conseq_state = []
      need_state = []
      
      result = ''
      key = ''
      value = ''
      d_dict = {}
      result_flag = False
      
      def __init__(self):
          print('')
          

      
      def 大纲(self):
            #er =tw
            all_dir = ['属性','性别','名字','称呼','姓名','小名','对象','行为','状态','结果'
                       ,'结构','用途','影响','特征','被影响','技能','后果'
                       ,'位置','变化','过去','现在','将来','种类','必需','需要'
                       ,'使用','内容','条件','理由','原因','方法','多余','好处'
                       ,'危害','关系','数量','能力','可行性','限制','疑问','目标'
                       ,'禁止','起源','期望','日常','否定','肯定','未知位置','确定位置'
                       ,'预设']
            return all_dir


      
      def 属性(self,multiple):
            
            global find_answer_flag      
            parameter = multiple
            t_judge = False
            result = ''
            sim_ref_value = 0.4
            
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               current_list = self.attribute_state   
               print('看看--->>>',parameter)
               print('关键☛☛☛☛', current_list,self.attribute_state)
               
               for clc,clk in enumerate(current_list):
                   for cdc,cdk in clk.items():
                       if parameter == cdc:
                          self.result = cdk                          
                          find_answer_flag = True
                          print('返回答案--键:',cdk)
                          return self.result
                          
                       elif parameter == cdk:
                          self.result = cdc
                          find_answer_flag = True
                          print('返回答案--值:',cdc)
                          return self.result
                          
                          
                       elif parameter in cdc:
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--相似键:',cdc)
                          return self.result

                       elif parameter in cdk:
                          self.result =  cdc + cdk
                          find_answer_flag = True
                          print('返回答案--相似值:',cdk)
                          return self.result

                       elif cdc in parameter:
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--键相似:',cdc)
                          return self.result

                       elif cdk in parameter :
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--值相似:',cdk)
                          return self.result

                       elif difflib.SequenceMatcher(None, cdc,parameter).ratio() >= sim_ref_value:
                            self.result = cdc
                            find_answer_flag = True
                            print('返回答案--值相似:',cdk)

                       elif difflib.SequenceMatcher(None, cdk,parameter).ratio() >= sim_ref_value:
                            self.result = cdk
                            find_answer_flag = True
                            print('返回答案--值相似:',cdk) 

                          
               #os.system("pause")
               
               return result#self.method_state#study_count
            
            else:
               #state.append(parameter)
               self.attribute_state.append(parameter)
               print('㊣㊣㊣㊣学习完成','♠♠♠♠子项:属性',self.attribute_state)
               #os.system("pause")
#---------------------------------------------------------------------------------------------------
      def 性别(self,multiple):
            
            global find_answer_flag      
            parameter = multiple
            t_judge = False
                                    
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               current_list = self.gender_state   
               print('看看--->>>',parameter)
               print('关键☛☛☛☛', current_list,self.gender_state)
               
               for clc,clk in enumerate(current_list):
                   for cdc,cdk in clk.items():
                       if parameter == cdc:
                          self.result = cdk                          
                          find_answer_flag = True
                          print('返回答案--键:',cdk)
                          return self.result
                          
                       elif parameter == cdk:
                          self.result = cdc
                          find_answer_flag = True
                          print('返回答案--值:',cdc)
                          return self.result
                          
                          
                       elif parameter in cdc:
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--相似键:',cdc)
                          return self.result

                       elif parameter in cdk:
                          self.result =  cdc + cdk
                          find_answer_flag = True
                          print('返回答案--相似值:',cdk)
                          return self.result

                       elif cdc in parameter:
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--键相似:',cdc)
                          return self.result

                       elif cdk in parameter :
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--值相似:',cdk)
                          return self.result

                          
               #os.system("pause")
               
               return result#self.method_state#study_count
            
            else:
               #state.append(parameter)
               self.gender_state.append(parameter)
               print('㊣㊣㊣㊣学习完成','♠♠♠♠子项:性别',self.gender_state)
               #os.system("pause")

#---------------------------------------------------------------------------------------------------               

      def 名字(self,multiple):
                  
            parameter = multiple
            t_judge = False
            
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:

               self.d_dict = self.call_state[0]
               for dc,dk in self.d_dict.items():
                   self.result = dc + dk


               return self.result
            
            else:
               self.call_state.append(parameter)
               print('㊣㊣㊣㊣学习完成''♠♠♠♠子项:名字',self.call_state)
               #os.system("pause") 

      def 姓名(self,multiple):
                  
            parameter = multiple
            t_judge = False
            
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               self.d_dict = self.call_state[0]
               for dc,dk in self.d_dict.items():
                   self.result = dc + dk
               
               return self.result
            
            else:
               self. call_state.append(parameter)
               print('㊣㊣㊣㊣学习完成','♠♠♠♠子项:姓名',self.call_state)
               #os.system("pause") 

      def 称呼(self,multiple):

            parameter = multiple
            t_judge = False
            
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               self.d_dict = self.call_state[0]
               for dc,dk in self.d_dict.items():
                   self.result = dc + dk
                   
               return self.result
            
            else:
               self.call_state.append(parameter)
               print('㊣㊣㊣㊣学习完成''♠♠♠♠子项:称呼',self.call_state)
               #os.system("pause") 

      def 小名(self,multiple):
                  
            call_state = []
            parameter = multiple
            t_judge = False
            
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               pass
            
            else:
               call_state.append(parameter)
               print('㊣㊣㊣㊣学习完成',call_state)
               #os.system("pause") 

      def 对象(self,multiple):

            parameter = multiple
            t_judge = False
            
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               self.d_dict = self.call_state[0]
               for dc,dk in self.d_dict.items():
                   self.result = dk
                   
               return self.result
            
            else:
               self.call_state.append(parameter)
               print('㊣㊣㊣㊣学习完成''♠♠♠♠子项:称呼',self.call_state)
               #os.system("pause") 

      def 行为(self,multiple):
            global find_answer_flag      
            parameter = multiple
            t_judge = False
            result = ''
            sim_ref_value = 0.6
            
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               current_list = self.action_state   
               print('看看--->>>',parameter)
               print('关键☛☛☛☛', current_list,self.action_state)
               
               for clc,clk in enumerate(current_list):
                   for cdc,cdk in clk.items():
                       if parameter == cdc:
                          self.result = cdk                          
                          find_answer_flag = True
                          print('返回答案--键:',cdk)
                          return self.result
                          
                       elif parameter == cdk:
                          self.result = cdc
                          find_answer_flag = True
                          print('返回答案--值:',cdc)
                          return self.result
                          
                          
                       elif parameter in cdc:
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--相似键:',cdc)
                          return self.result

                       elif parameter in cdk:
                          self.result =  cdc + cdk
                          find_answer_flag = True
                          print('返回答案--相似值:',cdk)
                          return self.result

                       elif cdc in parameter:
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--键相似:',cdc)
                          return self.result

                       elif cdk in parameter :
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--值相似:',cdk)
                          return self.result

                       elif difflib.SequenceMatcher(None, cdc,parameter).ratio() >= sim_ref_value:
                            self.result = cdc
                            find_answer_flag = True
                            print('返回答案--值相似:',cdk)

                       elif difflib.SequenceMatcher(None, cdk,parameter).ratio() >= sim_ref_value:
                            self.result = cdk
                            find_answer_flag = True
                            print('返回答案--值相似:',cdk) 

                          
               #os.system("pause")
               
               return result#self.method_state#study_count
            
            else:
               #state.append(parameter)
               self.action_state.append(parameter)
               print('㊣㊣㊣㊣学习完成','♠♠♠♠子项:行为',self.action_state)
               #os.system("pause")
      
      def 状态():
            describe = {}
            return describe
      
      def 条件(self,multiple):

            state = []
            parameter = multiple
            t_judge = False
            
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               pass
            
            else:
               state.append(parameter)
               print('㊣㊣㊣㊣学习完成','♠♠♠♠子项:条件',state)
               #os.system("pause")                
      
      def 结果(self,multiple):
            parameter = multiple
            t_judge = False
            sim_ref_value = 0.4
            result = ''
            
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               current_list = self.result_state   
               print('看看--->>>',parameter)
               print('关键☛☛☛☛', current_list,self.result_state)
               
               for clc,clk in enumerate(current_list):
                   for cdc,cdk in clk.items():
                       if parameter == cdc:
                          result = cdk                          
                          find_answer_flag = True
                          print('返回答案--键:',cdk)
                          
                       elif parameter == cdk:
                          result = cdc
                          find_answer_flag = True
                          print('返回答案--值:',cdc)
                          return result
                          
                       elif parameter in cdc:
                          result = cdk
                          find_answer_flag = True
                          print('返回答案--相似键:',cdk)
                          return result

                       elif parameter in cdk:
                          result = cdc
                          find_answer_flag = True
                          print('返回答案--相似值:',cdc)
                          return result

                       elif cdc in parameter:
                          result = cdk
                          find_answer_flag = True
                          print('返回答案--键相似:',cdk)
                          return result

                       elif cdk in parameter :
                          result = cdc
                          find_answer_flag = True
                          print('返回答案--值相似:',cdc)
                          return result

                       elif difflib.SequenceMatcher(None, cdc,parameter).ratio() >= sim_ref_value:
                            self.result = cdk
                            find_answer_flag = True
                            return self.result
                            print('返回答案--值相似:',cdk)

                       elif difflib.SequenceMatcher(None, cdk,parameter).ratio() >= sim_ref_value:
                            self.result = cdc
                            find_answer_flag = True
                            return self.result
                            print('返回答案--值相似:',cdc)   
                          
               #os.system("pause")
               
               return result#self.method_state#study_count
            
            else:
               #state.append(parameter)
               self.result_state.append(parameter)
               print('㊣㊣㊣㊣学习完成',self.result_state)
               #os.system("pause")

      def 后果(self,multiple):
            parameter = multiple
            t_judge = False
            sim_ref_value = 0.4
            result = ''
            
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               current_list = self.conseq_state   
               print('看看--->>>',parameter)
               print('关键☛☛☛☛', current_list,self.conseq_state)
               
               for clc,clk in enumerate(current_list):
                   for cdc,cdk in clk.items():
                       if parameter == cdc:
                          result = cdk                          
                          find_answer_flag = True
                          print('返回答案--键:',cdk)
                          
                       elif parameter == cdk:
                          result = cdc
                          find_answer_flag = True
                          print('返回答案--值:',cdc)
                          return result
                          
                       elif parameter in cdc:
                          result = cdk
                          find_answer_flag = True
                          print('返回答案--相似键:',cdk)
                          return result

                       elif parameter in cdk:
                          result = cdc
                          find_answer_flag = True
                          print('返回答案--相似值:',cdc)
                          return result

                       elif cdc in parameter:
                          result = cdk
                          find_answer_flag = True
                          print('返回答案--键相似:',cdk)
                          return result

                       elif cdk in parameter :
                          result = cdc
                          find_answer_flag = True
                          print('返回答案--值相似:',cdc)
                          return result

                       elif difflib.SequenceMatcher(None, cdc,parameter).ratio() >= sim_ref_value:
                            self.result = cdk
                            find_answer_flag = True
                            return self.result
                            print('返回答案--值相似:',cdk)

                       elif difflib.SequenceMatcher(None, cdk,parameter).ratio() >= sim_ref_value:
                            self.result = cdc
                            find_answer_flag = True
                            return self.result
                            print('返回答案--值相似:',cdk)  
                          
               #os.system("pause")
               
               return self.result#self.method_state#study_count
            
            else:
               #state.append(parameter)
               self.conseq_state.append(parameter)
               print('㊣㊣㊣㊣学习完成♣♣♣♣--子项:后果',self.conseq_state)
               #os.system("pause")         
      
      def 结构():
            state = {}
            return state

      
      
      def 用途():
            state = {}
            return state

      def 关系():
            state = {}
            return state

      def 起源(self,multiple):
                 
            global find_answer_flag      
            parameter = multiple
            t_judge = False            
                        
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               current_list = self.source_state   
               print('看看--->>>',parameter)
               print('关键☛☛☛☛', current_list,self.source_state)
               
               for clc,clk in enumerate(current_list):
                   for cdc,cdk in clk.items():
                       if parameter == cdc:
                          self.result = cdk                          
                          find_answer_flag = True
                          print('返回答案--键:',cdk)
                          #return self.result
                          
                       elif parameter == cdk:
                          self.result = cdc
                          find_answer_flag = True
                          print('返回答案--值:',cdc)
                          #return self.result
                          
                          
                       elif parameter in cdc:
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--相似键:',cdc)
                          #return self.result

                       elif parameter in cdk:
                          self.result =  cdc + cdk
                          find_answer_flag = True
                          print('返回答案--相似值:',cdk)
                          #return self.result

                       elif cdc in parameter:
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--键相似:',cdc)
                          #return self.result

                       elif cdk in parameter :
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--值相似:',cdk)
                          #return self.result
                          
               #os.system("pause")
               
               return self.result#self.method_state#study_count
            
            else:
               #state.append(parameter)
               self.source_state.append(parameter)
               print('㊣㊣㊣㊣学习完成','♠♠♠♠子项:起源',self.source_state)
               #os.system("pause")

      def 预设(self,multiple):

            global find_answer_flag      
            parameter = multiple
            t_judge = False
            result = ''
            sim_ref_value = 0.4
            story = '一个带狗的男子气势汹汹地对宠物商店的老板说,你把这条狗卖给我看门，昨天晚上小偷进我家偷了我300元钱,可这条狗连吭都没有吭一声,老板立即回答道：这条狗以前的主人是千百万富翁,这300元钱它根本不放在眼里'
            humor = '飞行员新兵训练，没一个敢跳伞，教练脸色难看，这时只见一个在傻偷笑，教练一脚把他踹下去了。这时一个个跟下饺子一样接二连三往下跳，教练纳闷了，拽住最后一个问，刚才让你们跳都不跳，怎么踹出去一个，你们都跳呀！新兵回道：教练你也赶紧跳吧，你踹出去的是驾驶员呀'
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            self.preset_state = [{'故事':story},{'笑话':humor}]
            
            if t_judge:
               current_list = self.preset_state   
               print('看看--->>>',parameter)
               print('关键☛☛☛☛', current_list,self.preset_state)
               
               for clc,clk in enumerate(current_list):
                   for cdc,cdk in clk.items():
                       if parameter == cdc:
                          self.result = cdk                          
                          find_answer_flag = True
                          print('返回答案--键:',cdk)
                          return self.result
                          
                       elif parameter == cdk:
                          self.result = cdc
                          find_answer_flag = True
                          print('返回答案--值:',cdc)
                          return self.result
                          
                          
                       elif parameter in cdc:
                          self.result = cdk
                          find_answer_flag = True
                          print('返回答案--相似键:',cdc)
                          return self.result

                       elif parameter in cdk:
                          self.result =  cdk
                          find_answer_flag = True
                          print('返回答案--相似值:',cdk)
                          return self.result

                       elif cdc in parameter:
                          self.result = cdk
                          find_answer_flag = True
                          print('返回答案--键相似:',cdc)
                          return self.result

                       elif cdk in parameter :
                          self.result = cdk
                          find_answer_flag = True
                          print('返回答案--值相似:',cdk)
                          return self.result

                       elif difflib.SequenceMatcher(None, cdc,parameter).ratio() >= sim_ref_value:
                            self.result = cdc
                            find_answer_flag = True
                            print('返回答案--值相似:',cdk)

                       elif difflib.SequenceMatcher(None, cdk,parameter).ratio() >= sim_ref_value:
                            self.result = cdk
                            find_answer_flag = True
                            print('返回答案--值相似:',cdk) 

                          
               #os.system("pause")
               
               return result#self.method_state#study_count
            
            else:
               #state.append(parameter)
               #self.preset_state.append(parameter)
               print('♨♨♨♨虚拟㊣㊣㊣㊣学习完成','♠♠♠♠子项:预设',self.preset_state)

      def 目标(self,multiple):
            
            global find_answer_flag      
            parameter = multiple
            t_judge = False
            result = ''
            sim_ref_value = 0.4
            
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               current_list = self.target_state   
               print('看看--->>>',parameter)
               print('关键☛☛☛☛', current_list,self.target_state)
               
               for clc,clk in enumerate(current_list):
                   for cdc,cdk in clk.items():
                       if parameter == cdc:
                          self.result = cdk                          
                          find_answer_flag = True
                          print('返回答案--键:',cdk)
                          return self.result
                          
                       elif parameter == cdk:
                          self.result = cdc
                          find_answer_flag = True
                          print('返回答案--值:',cdc)
                          return self.result
                          
                          
                       elif parameter in cdc:
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--相似键:',cdc)
                          return self.result

                       elif parameter in cdk:
                          self.result =  cdc + cdk
                          find_answer_flag = True
                          print('返回答案--相似值:',cdk)
                          return self.result

                       elif cdc in parameter:
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--键相似:',cdc)
                          return self.result

                       elif cdk in parameter :
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--值相似:',cdk)
                          return self.result

                       elif difflib.SequenceMatcher(None, cdc,parameter).ratio() >= sim_ref_value:
                            self.result = cdk
                            find_answer_flag = True
                            print('返回模糊答案--值相似:',cdk)
                            return self.result

                       elif difflib.SequenceMatcher(None, cdk,parameter).ratio() >= sim_ref_value:
                            self.result = cdk
                            find_answer_flag = True
                            print('返回模糊答案--值相似:',cdk)
                            return self.result

                          
               #os.system("pause")
               
               return result#self.method_state#study_count
            
            else:
               #state.append(parameter)
               self.target_state.append(parameter)
               print('㊣㊣㊣㊣学习完成','♠♠♠♠子项:目标',self.target_state)         
      
      def 期望():
                 
            state = {}
            return state

      

      def 影响():
            relevance = {}
                 
            return relevance

      def 被影响():
            state = {}
            return state

      def 技能(self,multiple):
            
            global find_answer_flag      
            parameter = multiple
            t_judge = False
            result = []
            sim_ref_value = 0.4
            
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               current_list = self.skill_state  
               print('看看--->>>',parameter)
               print('关键☛☛☛☛', current_list,self.skill_state)
               
               for clc,clk in enumerate(current_list):
                   for cdc,cdk in clk.items():
                       if parameter == cdc:
                          result.append(cdk)                          
                          find_answer_flag = True
                          print('返回答案--键:',cdk)
                          #return self.result
                          
                       elif parameter == cdk:
                          result.append(cdc)
                          find_answer_flag = True
                          print('返回答案--值:',cdc)
                          #return self.result
                          
                          
                       elif parameter in cdc:
                          result.append(cdk)
                          find_answer_flag = True
                          print('返回答案--相似键:',cdc)
                          #return self.result

                       elif parameter in cdk:
                          result.append(cdk)
                          find_answer_flag = True
                          print('返回答案--相似值:',cdk)
                          #return self.result

                       elif cdc in parameter:
                          result.append(cdc)
                          find_answer_flag = True
                          print('返回答案--键相似:',cdc)
                          #return self.result

                       elif cdk in parameter :
                          result.append(cdk)
                          find_answer_flag = True
                          print('返回答案--值相似:',cdk)
                          #return self.result

                       elif difflib.SequenceMatcher(None, cdc,parameter).ratio() >= sim_ref_value:
                            result.append(cdc)
                            find_answer_flag = True
                            #print('返回答案--值相似:',cdk)

                       elif difflib.SequenceMatcher(None, cdk,parameter).ratio() >= sim_ref_value:
                            result.append(cdk)
                            find_answer_flag = True
                            #print('返回答案--值相似:',cdk) 

                          
               #os.system("pause")
               
               return result#self.method_state#study_count
            
            else:
               #state.append(parameter)
               self.skill_state.append(parameter)
               print('㊣㊣㊣㊣学习完成','♠♠♠♠子项:技能',self.skill_state)
               #os.system("pause")
      
      def 特征():
            state = {}
            return state
      
      def 理由(self,multiple):
            state = []
            parameter = multiple
            t_judge = False
            
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               pass
            
            else:
               state.append(parameter)
               print('㊣㊣㊣㊣学习完成','♠♠♠♠子项:理由',state)
               #os.system("pause")

      def 原因(self,multiple):
            global find_answer_flag      
            parameter = multiple
            t_judge = False
            result_flag = False
                                    
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
                     
               current_list = self.cause_state
               print('看看--->>>',parameter)
               print('关键☛☛☛☛', current_list,self.cause_state)
               
               for clc,clk in enumerate(current_list):
                   for cdc,cdk in clk.items():
                       if parameter == cdc:
                          self.result = cdk                          
                          find_answer_flag = True
                          print('返回答案--键:',cdk)
                          return self.result
                          
                       elif parameter == cdk:
                          self.result = cdc
                          find_answer_flag = True
                          print('返回答案--值:',cdc)
                          return self.result
                          
                          
                       elif parameter in cdc:
                          self.result = cdk
                          find_answer_flag = True
                          print('返回答案--相似键:',cdc)
                          return self.result

                       elif parameter in cdk:
                          self.result =  cdc
                          find_answer_flag = True
                          print('返回答案--相似值:',cdk)
                          return self.result

                       elif cdc in parameter:
                          self.result = cdk
                          find_answer_flag = True
                          print('返回答案--键相似:',cdc)
                          return self.result

                       elif cdk in parameter :
                          self.result = cdc
                          find_answer_flag = True
                          print('返回答案--值相似:',cdk)
                          return self.result

               if find_answer_flag == False:
                  result_flag = False
                  
                  return result_flag
               #os.system("pause")   

            
            else:
               #state.append(parameter)
               self.cause_state.append(parameter)
               print('㊣㊣㊣㊣学习完成','♠♠♠♠子项:原因',self.cause_state)
               #os.system("pause")
      
      def 位置(self,multiple):
            global find_answer_flag      
            parameter = multiple
            t_judge = False
                                    
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               current_list = self.location_state  
               print('看看--->>>',parameter)
               print('关键☛☛☛☛', current_list,self.location_state)
               
               for clc,clk in enumerate(current_list):
                   for cdc,cdk in clk.items():
                       if parameter == cdc:
                          self.result = cdk                          
                          find_answer_flag = True
                          print('返回答案--键:',cdk)
                          return self.result
                          
                       elif parameter == cdk:
                          self.result = cdc
                          find_answer_flag = True
                          print('返回答案--值:',cdc)
                          return self.result
                          
                          
                       elif parameter in cdc:
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--相似键:',cdc)
                          return self.result

                       elif parameter in cdk:
                          self.result =  cdc + cdk
                          find_answer_flag = True
                          print('返回答案--相似值:',cdk)
                          return self.result

                       elif cdc in parameter:
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--键相似:',cdc)
                          return self.result

                       elif cdk in parameter :
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--值相似:',cdk)
                          return self.result
                       #else:                          
               #os.system("pause")
               
               return result#self.method_state#study_count
            
            else:
               #state.append(parameter)
               self.location_state.append(parameter)
               print('㊣㊣㊣㊣学习完成','♠♠♠♠子项:位置',self.location_state)
               #os.system("pause")
      
      def 变化():
          state = {}
          return state   
      
      def 需要(self,multiple):
            
          global find_answer_flag
          global force_out_ansewr
          parameter = multiple
          t_judge = False
          result = ''
          sim_ref_value = 0.4
            
          t_judge = isinstance(parameter, str)#判断属于字符或字典
            
          if t_judge:
               current_list = self.need_state   
               print('看看--->>>',parameter)
               print('关键☛☛☛☛', current_list,self.need_state)
               
               for clc,clk in enumerate(current_list):
                   for cdc,cdk in clk.items():
                       if parameter == cdc:
                          self.result = cdk                          
                          find_answer_flag = True
                          print('返回答案--键:',cdk)
                          #return self.result
                          
                       elif parameter == cdk:
                          self.result = cdc
                          find_answer_flag = True
                          print('返回答案--值:',cdc)
                          #return self.result
                          
                          
                       elif parameter in cdc:
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--相似键:',cdc)
                          #return self.result

                       elif parameter in cdk:
                          self.result =  cdc + cdk
                          find_answer_flag = True
                          print('返回答案--相似值:',cdk)
                          #return self.result

                       elif cdc in parameter:
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--键相似:',cdc)
                          #return self.result

                       elif cdk in parameter :
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--值相似:',cdk)
                          

                       elif difflib.SequenceMatcher(None, cdc,parameter).ratio() >= sim_ref_value:
                            self.result = cdc
                            find_answer_flag = True
                            print('返回答案--值相似:',cdk)

                       elif difflib.SequenceMatcher(None, cdk,parameter).ratio() >= sim_ref_value:
                            self.result = cdk
                            find_answer_flag = True
                            print('返回答案--值相似:',cdk) 

                          
               #os.system("pause")
               if find_answer_flag:
                  return self.result
            
               else:
                     
                  if force_out_ansewr:
                     return self.need_state
                  
                  else:
            
                      return find_answer_flag#self.method_state#study_count
            
          else:
               #state.append(parameter)
               self.need_state.append(parameter)
               print('㊣㊣㊣㊣学习完成','♠♠♠♠子项:需要',self.need_state)
               #os.system("pause")

      def 使用(self,multiple):
            
            global find_answer_flag      
            parameter = multiple
            t_judge = False
            sim_ref_value = 0.4                        
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               current_list = self.use_state   
               print('看看--->>>',parameter)
               print('关键☛☛☛☛', current_list,self.use_state)
               
               for clc,clk in enumerate(current_list):
                   for cdc,cdk in clk.items():
                       if parameter == cdc:
                          self.result = cdk                          
                          find_answer_flag = True
                          print('返回答案--键:',cdk)
                          return self.result
                          
                       elif parameter == cdk:
                          self.result = cdc
                          find_answer_flag = True
                          print('返回答案--值:',cdc)
                          return self.result
                          
                          
                       elif parameter in cdc:
                          self.result = cdc
                          find_answer_flag = True
                          print('返回答案--相似键:',cdc)
                          return self.result

                       elif parameter in cdk:
                          self.result =  cdk
                          find_answer_flag = True
                          print('返回答案--相似值:',cdk)
                          return self.result

                       elif cdc in parameter:
                          self.result = cdk
                          find_answer_flag = True
                          print('返回答案--键相似:',cdk)
                          return self.result

                       elif cdk in parameter :
                          self.result = cdc
                          find_answer_flag = True
                          print('返回答案--值相似:',cdc)
                          return self.result

                       elif difflib.SequenceMatcher(None, cdc,parameter).ratio() >= sim_ref_value:
                            self.result = cdc
                            find_answer_flag = True
                            print('返回答案--值相似:',cdk)

                       elif difflib.SequenceMatcher(None, cdk,parameter).ratio() >= sim_ref_value:
                            self.result = cdk
                            find_answer_flag = True
                            print('返回答案--值相似:',cdk)                    
                          
               #os.system("pause")
               
               return self.result#self.method_state#study_count
            
            else:
               #state.append(parameter)
               self.use_state.append(parameter)
               print('㊣㊣㊣㊣学习完成','♠♠♠♠子项:使用',self.use_state)
               #os.system("pause")
      
      def 必需():
                 
            state = {}
            return state
      
      def 方法(self,multiple):
            
            global study_count           
            global find_answer_flag
            parameter = multiple
            t_judge = False
            result = ''
            
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               current_list = self.method_state 
               print('看看--->>>',parameter)
               print('关键☛☛☛☛', current_list,self.method_state)
               
               for clc,clk in enumerate(current_list):
                   for cdc,cdk in clk.items():
                       if parameter == cdc:
                          result = cdk                          
                          find_answer_flag = True
                          print('返回答案--键:',cdk)
                          
                       elif parameter == cdk:
                          result = cdc
                          find_answer_flag = True
                          print('返回答案--值:',cdc)
                          return result
                          
                       elif parameter in cdc:
                          result = cdk
                          find_answer_flag = True
                          print('返回答案--相似键:',cdk)
                          return result

                       elif parameter in cdk:
                          result = cdc
                          find_answer_flag = True
                          print('返回答案--相似值:',cdc)
                          return result

                       elif cdc in parameter:
                          result = cdk
                          find_answer_flag = True
                          print('返回答案--键相似:',cdk)
                          return result

                       elif cdk in parameter :
                          result = cdc
                          find_answer_flag = True
                          print('返回答案--值相似:',cdc)
                          return result

                       elif difflib.SequenceMatcher(None, cdc,parameter).ratio() >= sim_ref_value:
                            self.result = cdk
                            find_answer_flag = True
                            return self.result
                            print('返回答案--值相似:',cdk)

                       elif difflib.SequenceMatcher(None, cdk,parameter).ratio() >= sim_ref_value:
                            self.result = cdc
                            find_answer_flag = True
                            return self.result
                            print('返回答案--值相似:',cdc)
                      
               if find_answer_flag == False:
                  return  find_answer_flag  
                     

            else:
               #state.append(parameter)
               self.use_state.append(parameter)
               print('㊣㊣㊣㊣学习完成','♠♠♠♠子项:方法',self.method_state)
               #os.system("pause")          
               

      def 内容(self,multiple):
            
            global find_answer_flag

            state = []
            parameter = multiple
            t_judge = False
            
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               pass
            
            else:
               state.append(parameter)
               print('㊣㊣㊣㊣学习完成',state)
               #os.system("pause")
      
      def 过去():
            state = {}
            return state

      def 现在():
            state = {}
            return state

      def 将来():
            state = {}
            return state

      def 种类():
            state = {}
            return state

      def 数量(self,multiple):
            state = []
            return state

      def 多余():
                 
            state = {}
            return state
      def 好处():
                 
            state = {}
            return state

      def 危害():
                 
            state = {}
            return state

      def 归属():
                 
                   
            state = {}
            return state

      def 权限():
                 
                   
            state = {}
            return state

      def 允许():
                 
                   
            state = {}
            return state

      def 禁止():
                 
                   
            state = {}
            return state
      
      def 否定(self,multiple):

            parameter = multiple
            t_judge = False
            
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               pass
            
            else:
               self.call_state.append(parameter)
               print('㊣㊣㊣㊣学习完成',self.call_state)
               #os.system("pause") 
   

      def 标签():
          label = '反向人称描述'
          return label
#//////////////////////////////////////////////////////////////////////////////////////////////////////////
class  电脑(object):
      
      def __init__(self):
          print("")

      global obj_flag
      global storage_usr_info
      #global current_key_word_obj
      global usr_in_word_len
      global mood
      global reason      
      method_state = []
      result_state = []
      call_state   = []
      attribute_state = []
      source_state = []
      gender_state = []
      
      result = ''
      key = ''
      value = ''
      d_dict = {}
      
      def __init__(self):
          print('')

          
      def 对象():
          obj = ['我','你','人类']
          return obj
      
      def 大纲(self):
            #er =tw
            all_dir = ['属性','称呼','行为','状态','结果','结构','用途','影响','特征','被影响'
                       ,'位置','变化','过去','现在','将来','种类','必需','需要'
                       ,'内容','条件','理由','原因','方法','多余','好处','危害','关系','数量'
                       ,'起源','期望','日常','未知位置','确定位置']
            return all_dir


      
      def 属性(self,multiple):
            
            global find_answer_flag      
            parameter = multiple
            t_judge = False
            
                        
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               current_list = self.attribute_state   
               print('看看--->>>',parameter)
               print('关键☛☛☛☛', current_list,self.attribute_state)
               
               for clc,clk in enumerate(current_list):
                   for cdc,cdk in clk.items():
                       if parameter == cdc:
                          self.result = cdk                          
                          find_answer_flag = True
                          print('返回答案--键:',cdk)
                          return self.result
                          
                       elif parameter == cdk:
                          self.result = cdc
                          find_answer_flag = True
                          print('返回答案--值:',cdc)
                          return self.result
                          
                          
                       elif parameter in cdc:
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--相似键:',cdc)
                          return self.result

                       elif parameter in cdk:
                          self.result =  cdc + cdk
                          find_answer_flag = True
                          print('返回答案--相似值:',cdk)
                          return self.result

                       elif cdc in parameter:
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--键相似:',cdc)
                          return self.result

                       elif cdk in parameter :
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--值相似:',cdk)
                          return self.result

                       #else:

                          
               #os.system("pause")
               
               return result#self.method_state#study_count
            
            else:
               #state.append(parameter)
               self.attribute_state.append(parameter)
               print('㊣㊣㊣㊣学习完成','♠♠♠♠子项:属性',self.attribute_state)
               #os.system("pause")

      def 称呼(self,multiple):

            parameter = multiple
            t_judge = False
            
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               pass
            
            else:
               self.call_state.append(parameter)
               print('㊣㊣㊣㊣学习完成',self.call_state)
               #os.system("pause") 
     

      def 行为():
            state = {}
            return state
      
      def 状态():
            describe = {}
            return describe
      
      def 条件(self,multiple):

            state = []
            parameter = multiple
            t_judge = False
            
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               pass
            
            else:
               state.append(parameter)
               print('㊣㊣㊣㊣学习完成',state)
               #os.system("pause")                
      
      def 结果(self,multiple):
            parameter = multiple
            t_judge = False
            result = ''
            
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               current_list = self.result_state   
               print('看看--->>>',parameter)
               print('关键☛☛☛☛', current_list,self.result_state)
               
               for clc,clk in enumerate(current_list):
                   for cdc,cdk in clk.items():
                       if parameter == cdc:
                          result = cdk                          
                          find_answer_flag = True
                          print('返回答案--键:',cdk)
                          
                       elif parameter == cdk:
                          result = cdc
                          find_answer_flag = True
                          print('返回答案--值:',cdc)
                          return result
                          
                       elif parameter in cdc:
                          result = cdk
                          find_answer_flag = True
                          print('返回答案--相似键:',cdk)
                          return result

                       elif parameter in cdk:
                          result = cdc
                          find_answer_flag = True
                          print('返回答案--相似值:',cdc)
                          return result

                       elif cdc in parameter:
                          result = cdk
                          find_answer_flag = True
                          print('返回答案--键相似:',cdk)
                          return result

                       elif cdk in parameter :
                          result = cdc
                          find_answer_flag = True
                          print('返回答案--值相似:',cdc)
                          return result
                          
               #os.system("pause")
               
               return result#self.method_state#study_count
            
            else:
               #state.append(parameter)
               self.result_state.append(parameter)
               print('㊣㊣㊣㊣学习完成',self.result_state)
               #os.system("pause")
      
      def 结构():
            state = {}
            return state
      
      def 用途():
            state = {}
            return state

      def 关系():
            state = {}
            return state

      def 起源(self,multiple):
                 
            global find_answer_flag      
            parameter = multiple
            t_judge = False            
                        
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               current_list = self.source_state   
               print('看看--->>>',parameter)
               print('关键☛☛☛☛', current_list,self.source_state)
               
               for clc,clk in enumerate(current_list):
                   for cdc,cdk in clk.items():
                       if parameter == cdc:
                          self.result = cdk                          
                          find_answer_flag = True
                          print('返回答案--键:',cdk)
                          return self.result
                          
                       elif parameter == cdk:
                          self.result = cdc
                          find_answer_flag = True
                          print('返回答案--值:',cdc)
                          return self.result
                          
                          
                       elif parameter in cdc:
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--相似键:',cdc)
                          return self.result

                       elif parameter in cdk:
                          self.result =  cdc + cdk
                          find_answer_flag = True
                          print('返回答案--相似值:',cdk)
                          return self.result

                       elif cdc in parameter:
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--键相似:',cdc)
                          return self.result

                       elif cdk in parameter :
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--值相似:',cdk)
                          return self.result
                          
               #os.system("pause")
               
               return result#self.method_state#study_count
            
            else:
               #state.append(parameter)
               self.source_state.append(parameter)
               print('㊣㊣㊣㊣学习完成','♠♠♠♠子项:起源',self.source_state)
               #os.system("pause")
      
      def 期望():
                 
            state = {}
            return state

      

      def 影响():
            relevance = {}
                 
            return relevance

      def 被影响():
            state = {}
            return state
      
      def 特征():
            state = {}
            return state
      
      def 理由(self,multiple):
            state = []
            parameter = multiple
            t_judge = False
            
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               pass
            
            else:
               state.append(parameter)
               print('㊣㊣㊣㊣学习完成',state)
               #os.system("pause")

      def 原因(self,multiple):
            state = []
            parameter = multiple
            t_judge = False
            
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               pass
            
            else:
               state.append(parameter)
               print('㊣㊣㊣㊣学习完成',state)
               #os.system("pause")
      
      def 位置():
            state = {}
            
            return state
      
      def 变化():
            state = {}
            return state
      
      def 需要():
            state = []
            parameter = multiple
            t_judge = False
            
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               pass
            
            else:
               state.append(parameter)
               print('㊣㊣㊣㊣学习完成',state)
               #os.system("pause")
            
            return state
      
      def 必需():
                 
            state = {}
            return state
      
      def 方法(self,multiple):
            
            global study_count           
            
            parameter = multiple
            t_judge = False
            result = ''
            
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               current_list = self.method_state   
               print('看看--->>>',parameter)
               print('关键☛☛☛☛', current_list,self.method_state)
               
               for clc,clk in enumerate(current_list):
                   for cdc,cdk in clk.items():
                       if parameter == cdc:
                          result = cdk                          
                          find_answer_flag = True
                          print('返回答案--键:',cdk)
                          
                       elif parameter == cdk:
                          result = cdc
                          find_answer_flag = True
                          print('返回答案--值:',cdc)
                          return result
                          
                       elif parameter in cdc:
                          result = cdk
                          find_answer_flag = True
                          print('返回答案--相似键:',cdk)
                          return result

                       elif parameter in cdk:
                          result = cdc
                          find_answer_flag = True
                          print('返回答案--相似值:',cdc)
                          return result

                       elif cdc in parameter:
                          result = cdk
                          find_answer_flag = True
                          print('返回答案--键相似:',cdk)
                          return result

                       elif cdk in parameter :
                          result = cdc
                          find_answer_flag = True
                          print('返回答案--值相似:',cdc)
                          return result
                          
               #os.system("pause")
               
               return result#self.method_state#study_count

            
            else:
               study_count.append(parameter)
               self.method_state.append(parameter)
               #current_list = self.method_state
               print('㊣㊣㊣㊣学习完成',study_count,self.method_state)
               #study_count = state
               #os.system("pause")
               

      def 内容(self,multiple):

            state = []
            parameter = multiple
            t_judge = False
            
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               pass
            
            else:
               state.append(parameter)
               print('㊣㊣㊣㊣学习完成',state)
               #os.system("pause")
      
      def 过去():
            state = {}
            return state

      def 现在():
            state = {}
            return state

      def 将来():
            state = {}
            return state

      def 种类():
            state = {}
            return state

      def 数量(self,multiple):
            state = []
            return state

      def 多余():
                 
            state = {}
            return state
      def 好处():
                 
            state = {}
            return state

      def 危害():
                 
            state = {}
            return state

      def 归属():
                 
                   
            state = {}
            return state

      def 权限():
                 
                   
            state = {}
            return state

      def 允许():
                 
                   
            state = {}
            return state

      def 禁止():
                 
                   
            state = {}
            return state
   

      def 标签():
          label = '电脑'
          return label      
#---------------------------------------------------------------------------------------------------
class  代码(object):
      global obj_flag
      global storage_usr_info
      #global current_key_word_obj
      global usr_in_word_len
      r_parameter = ''

      def __init__(self):
          print('')
          
      def 对象(self):
          print('')
          
      def 标签():
          label = '编码'
          return label      
#---------------------------------------------------------------------------------------------------                     

      
#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class 玩乐(object):

       global storage_usr_info
      #global current_key_word_obj
       global usr_in_word_len
       
       
       r_parameter = ''

       def __init__(self):
          print('')
          
       def 对象(self):
          print('测试>>>玩:一种放松的行为')
          
       def obj():
          c_obj_flag = False          
          global conversion_usr_info
          global conversion_count
          global obj_flag_c
          global obj_flag_list
          global obj_flag
          global current_key_word_obj
          global conversion_person_key_word
          count_usr_info = 0
          count_usr_info = len(conversion_usr_info)
#--------------------------------------------------------------------------------------------------          
#--------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------- ---         
          
#////////////////////////////////////////////////////////////////////////////////////////////////////
class 买(object):
     
      
      global obj_flag
      global storage_usr_info
      global usr_in_word_len
      global mood
      global reason      
      r_parameter = ''
      def __init__(self):
          print('')

      
      def 大纲(self):
            #er =tw
            all_dir = ['描述','行为','对象','状态','结果','结构','用途','影响','特征','被影响'
                       ,'理由','位置','变化','过去','现在','将来','种类','必需','需要'
                       ,'理由','方法','多余','好处','危害','关系','起源'
                       ,'期望','数量','未知位置','确定位置']
            return all_dir
      
      def 描述():
                 
            state = {}
            return state

      def 行为():
            state = {}
            return state

      def 对象():
            state = {}
            return state
      
      def 状态():
            describe = {}
            return describe
      
      def 结果():
            state = {}
            return state
      
      def 结构():
            state = {}
            return state
      
      def 用途():
            state = {}
            return state

      def 关系():
            state = {}
            return state

      def 起源():
                 

            state = {}
            return state
      
      def 期望():
                 

            state = {}
            return state
      
      

      def 影响():
            relevance ={}
                 
            return relevance

      def 被影响():
            state = {}
            return state
      
      def 特征():
            state = {}
            return state
      
      def 理由():
            state = {}
            return state
      def 位置():
            state = {}
            return state
      
      def 变化():
            state = {}
            return state
      
      def 需要():
                 

            state = {}
            return state
      def 必需():
                 
 
            state = {}
            return state
      
      def 方法():

            state = {}
            return state
      
      def 过去():
            state = {}
            return state

      def 现在():
            state = {}
            return state

      def 将来():
            state = {}
            return state

      def 种类():
            state = {}
            return state

      def 多余():
                 
            state = {}
            return state
      def 好处():
                 
            state = {}
            return state

      def 危害():
                 
            state = {}
            return state

      def 归属():
                 
                   
            state = {}
            return state

      def 权限():
                 
                   
            state = {}
            return state

      def 允许():
                 
                   
            state = {}
            return state

      def 禁止():
                 
                   
            state = {}
            return state

      def 数量():
            state = {}
            return state

      def 标签():
            label = '买'
            return label


      def 未知位置():
            state = {}
            return state

      def 确定位置():
            state = {}
            return state

#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class  你(object):
      
      global obj_flag
      global storage_usr_info
      #global current_key_word_obj
      global usr_in_word_len
      global mood
      global reason      
      method_state = []
      result_state = []
      hight_state = []
      weight_state = []
      emotion_state = []
      result = ''
      
      def __init__(self):
          print('')
          

      
      def 大纲(self):
            #er =tw
            all_dir = ['描述','行为','状态','结果','结构','身高','体重','用途','影响'
                       ,'特征','被影响','位置','变化','过去','现在','将来','种类'
                       ,'必需','需要','内容','条件','理由','原因','方法','多余'
                       ,'好处','危害','关系','数量','情绪'
                       ,'起源','期望','日常','未知位置','确定位置']
            return all_dir

      def 对象():
          obj = []
          return obj
      
      def 描述():
                  
            state = {}
            return state

      def 行为():
            state = {}
            return state
      
      def 状态():
            describe = {}
            return describe
      
      def 条件(self,multiple):

            state = []
            parameter = multiple
            t_judge = False
            global find_answer_flag
            
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               pass
            
            else:
               state.append(parameter)
               print('㊣㊣㊣㊣学习完成',state)
               #os.system("pause")                
      
      def 结果(self,multiple):
            #global study_count           
            sim_ref_value = 0.4
            parameter = multiple
            t_judge = False
            result = ''
            global find_answer_flag
            
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               current_list = self.method_state   
               print('看看--->>>',parameter)
               print('关键☛☛☛☛', current_list,self.method_state)
               
               for clc,clk in enumerate(current_list):
                   for cdc,cdk in clk.items():
                       if parameter == cdc:
                          result = cdk
                          find_answer_flag = True
                          print('返回答案--键:',cdk)
                          
                       elif parameter == cdk:
                          result = cdc
                          find_answer_flag = True
                          print('返回答案--值:',cdc)
                          
                       elif parameter in cdc:
                          result = cdk   
                          print('返回答案--相似键:',cdk)

                       elif parameter in cdk:
                          result = cdc
                          find_answer_flag = True
                          print('返回答案--相似值:',cdc)

                       elif cdc in parameter:
                          result = cdk
                          find_answer_flag = True
                          print('返回答案--键相似:',cdk)

                       elif cdk in parameter :
                          result = cdc
                          find_answer_flag = True
                          print('返回答案--值相似:',cdc)

                       elif difflib.SequenceMatcher(None, cdc,parameter).ratio() >= sim_ref_value:
                            result = cdk
                            find_answer_flag = True
                            print('返回答案--值相似:',cdc)

                       elif difflib.SequenceMatcher(None, cdk,parameter).ratio() >= sim_ref_value:
                            result = cdc
                            find_answer_flag = True
                            print('返回答案--值相似:',cdc)
                            
                       else:
                            print('✘✘✘✘解析答案失败')

               print('☛☛☛☛看相似度:')
                     #,sim_sub_list)
               #result = sim_sub_list[sim_loc]
               return result#self.method_state#study_count
            
            else:
               #state.append(parameter)
               self.result_state.append(parameter)
               print('㊣㊣㊣㊣学习完成',self.result_state)
               #os.system("pause")
      
      def 结构():
            state = {}
            return state

      def 身高(self,multiple):
            
            global find_answer_flag      
            parameter = multiple
            t_judge = False
            result_flag = False
                                    
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
                     
               current_list = self.hight_state   
               print('看看--->>>',parameter)
               print('关键☛☛☛☛', current_list,self.hight_state)
               
               for clc,clk in enumerate(current_list):
                   for cdc,cdk in clk.items():
                       if parameter == cdc:
                          self.result = cdk                          
                          find_answer_flag = True
                          print('返回答案--键:',cdk)
                          return self.result
                          
                       elif parameter == cdk:
                          self.result = cdc
                          find_answer_flag = True
                          print('返回答案--值:',cdc)
                          return self.result
                          
                          
                       elif parameter in cdc:
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--相似键:',cdc)
                          return self.result

                       elif parameter in cdk:
                          self.result =  cdc + cdk
                          find_answer_flag = True
                          print('返回答案--相似值:',cdk)
                          return self.result

                       elif cdc in parameter:
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--键相似:',cdc)
                          return self.result

                       elif cdk in parameter :
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--值相似:',cdk)
                          return self.result

               if find_answer_flag == False:
                  result_flag = False
                  
                  return result_flag
               #os.system("pause")   
               
               #return result
            
            else:
               #state.append(parameter)
               self.hight_state.append(parameter)
               print('㊣㊣㊣㊣学习完成','♠♠♠♠子项:身高',self.hight_state)
               #os.system("pause")

      def 体重(self,multiple):
            global find_answer_flag      
            parameter = multiple
            t_judge = False
                                    
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               current_list = self.weight_state   
               print('看看--->>>',parameter)
               print('关键☛☛☛☛', current_list,self.weight_state)
               
               for clc,clk in enumerate(current_list):
                   for cdc,cdk in clk.items():
                       if parameter == cdc:
                          self.result = cdk                          
                          find_answer_flag = True
                          print('返回答案--键:',cdk)
                          return self.result
                          
                       elif parameter == cdk:
                          self.result = cdc
                          find_answer_flag = True
                          print('返回答案--值:',cdc)
                          return self.result
                          
                          
                       elif parameter in cdc:
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--相似键:',cdc)
                          return self.result

                       elif parameter in cdk:
                          self.result =  cdc + cdk
                          find_answer_flag = True
                          print('返回答案--相似值:',cdk)
                          return self.result

                       elif cdc in parameter:
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--键相似:',cdc)
                          return self.result

                       elif cdk in parameter :
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--值相似:',cdk)
                          return self.result

                          
               #os.system("pause")
               
               return result#self.method_state#study_count
            
            else:
               #state.append(parameter)
               self.highe_state.append(parameter)
               print('㊣㊣㊣㊣学习完成','♠♠♠♠子项:体重',self.weight_state)
               #os.system("pause")
      
      def 用途():
            state = {}
            return state

      def 关系():
            state = {}
            return state

      def 起源():
                 
            state = {}
            return state
      
      def 期望():
                 
            state = {}
            return state

      

      def 影响():
            relevance = {}
                 
            return relevance

      def 被影响():
            state = {}
            return state
      
      def 特征():
            state = {}
            return state
      
      def 理由(self,multiple):
            state = []
            parameter = multiple
            t_judge = False
            global find_answer_flag
            
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               current_list = self.method_state   
               print('看看--->>>',parameter)
               print('关键☛☛☛☛', current_list,self.method_state)
               
               for clc,clk in enumerate(current_list):
                   for cdc,cdk in clk.items():
                       if parameter == cdc:
                          result = cdk
                          find_answer_flag = True
                          print('返回答案--键:',cdk)
                          
                       elif parameter == cdk:
                          result = cdc
                          find_answer_flag = True
                          print('返回答案--值:',cdc)
                          
                       elif parameter in cdc:
                          result = cdk   
                          print('返回答案--相似键:',cdk)

                       elif parameter in cdk:
                          result = cdc
                          find_answer_flag = True
                          print('返回答案--相似值:',cdc)

                       elif cdc in parameter:
                          result = cdk
                          find_answer_flag = True
                          print('返回答案--键相似:',cdk)

                       elif cdk in parameter :
                          result = cdc
                          find_answer_flag = True
                          print('返回答案--值相似:',cdc)

                       elif difflib.SequenceMatcher(None, cdc,parameter).ratio() >= sim_ref_value:
                            result = cdk
                            find_answer_flag = True
                            print('返回答案--值相似:',cdc)

                       elif difflib.SequenceMatcher(None, cdk,parameter).ratio() >= sim_ref_value:
                            result = cdc
                            find_answer_flag = True
                            print('返回答案--值相似:',cdc)     
                          

               print('☛☛☛☛看相似度:')
                     #,sim_sub_list)
               #result = sim_sub_list[sim_loc]
               return result#self.method_state#study_count
            
            else:
               state.append(parameter)
               print('㊣㊣㊣㊣学习完成',state)
               #os.system("pause")

      def 原因(self,multiple):
            state = []
            parameter = multiple
            t_judge = False
            global find_answer_flag
            
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               pass
            
            else:
               state.append(parameter)
               print('㊣㊣㊣㊣学习完成',state)
               #os.system("pause")
      
      def 位置():
            state = {}
            
            return state
      
      def 变化():
            state = {}
            return state
      
      def 需要():
            state = []
            parameter = multiple
            t_judge = False
            global find_answer_flag
            
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               pass
            
            else:
               state.append(parameter)
               print('㊣㊣㊣㊣学习完成',state)
               #os.system("pause")
            
            return state
      
      def 必需():
                 
            state = {}
            return state
      
      def 方法(self,multiple):
            
            global study_count
            global find_answer_flag

            sim_ref_value = 0.4
            parameter = multiple
            t_judge = False
            result = ''
            
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               current_list = self.method_state   
               print('看看--->>>',parameter)
               print('关键☛☛☛☛', current_list,self.method_state)
               
               for clc,clk in enumerate(current_list):
                   for cdc,cdk in clk.items():
                       if parameter == cdc:
                          result = cdk
                          find_answer_flag = True
                          print('返回答案--键:',cdk)
                          
                       elif parameter == cdk:
                          result = cdc
                          find_answer_flag = True
                          print('返回答案--值:',cdc)
                          
                       elif parameter in cdc:
                          result = cdk   
                          print('返回答案--相似键:',cdk)

                       elif parameter in cdk:
                          result = cdc
                          find_answer_flag = True
                          print('返回答案--相似值:',cdc)

                       elif cdc in parameter:
                          result = cdk
                          find_answer_flag = True
                          print('返回答案--键相似:',cdk)

                       elif cdk in parameter :
                          result = cdc
                          find_answer_flag = True
                          print('返回答案--值相似:',cdc)

                       elif difflib.SequenceMatcher(None, cdc,parameter).ratio() >= sim_ref_value:
                            result = cdk
                            find_answer_flag = True
                            print('返回答案--值相似:',cdc)

                       elif difflib.SequenceMatcher(None, cdk,parameter).ratio() >= sim_ref_value:
                            result = cdc
                            find_answer_flag = True
                            print('返回答案--值相似:',cdc)     
                          
               
               #print('☛☛☛☛看相似度:')
                     #,sim_sub_list)
               #result = sim_sub_list[sim_loc]
               return result#self.method_state#study_count

            
            else:
               study_count.append(parameter)
               self.method_state.append(parameter)
               #current_list = self.method_state
               print('㊣㊣㊣㊣学习完成','♠♠♠♠对应子项:方法',study_count,self.method_state)
               #study_count = state
               #os.system("pause")
               

      def 内容(self,multiple):

            state = []
            parameter = multiple
            t_judge = False
            
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               pass
            
            else:
               state.append(parameter)
               print('㊣㊣㊣㊣学习完成',state)
               #os.system("pause")
      
      def 过去():
            state = {}
            return state

      def 现在():
            state = {}
            return state

      def 将来():
            state = {}
            return state

      def 种类():
            state = {}
            return state

      def 数量(self,multiple):
            state = []
            return state

      def 情绪(self,multiple):
            
            global find_answer_flag      
            parameter = multiple
            t_judge = False
            result = ''
            sim_ref_value = 0.4
            
            t_judge = isinstance(parameter, str)#判断属于字符或字典
            
            if t_judge:
               current_list = self.emotion_state   
               print('看看--->>>',parameter)
               print('关键☛☛☛☛', current_list,self.emotion_state)
               
               for clc,clk in enumerate(current_list):
                   for cdc,cdk in clk.items():
                       if parameter == cdc:
                          self.result = cdk                          
                          find_answer_flag = True
                          print('返回答案--键:',cdk)
                          return self.result
                          
                       elif parameter == cdk:
                          self.result = cdc
                          find_answer_flag = True
                          print('返回答案--值:',cdc)
                          return self.result
                          
                          
                       elif parameter in cdc:
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--相似键:',cdc)
                          return self.result

                       elif parameter in cdk:
                          self.result =  cdc + cdk
                          find_answer_flag = True
                          print('返回答案--相似值:',cdk)
                          return self.result

                       elif cdc in parameter:
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--键相似:',cdc)
                          return self.result

                       elif cdk in parameter :
                          self.result = cdc + cdk
                          find_answer_flag = True
                          print('返回答案--值相似:',cdk)
                          return self.result

                       elif difflib.SequenceMatcher(None, cdc,parameter).ratio() >= sim_ref_value:
                            self.result = cdc
                            find_answer_flag = True
                            print('返回答案--值相似:',cdk)

                       elif difflib.SequenceMatcher(None, cdk,parameter).ratio() >= sim_ref_value:
                            self.result = cdk
                            find_answer_flag = True
                            print('返回答案--值相似:',cdk) 

                          
               #os.system("pause")
               if find_answer_flag == False:
                     
                  return find_answer_flag#self.method_state#study_count
            
            else:
               #state.append(parameter)
               self.emotion_state.append(parameter)
               print('㊣㊣㊣㊣学习完成','♠♠♠♠子项:情绪',self.emotion_state)
               #os.system("pause")

      def 多余():
                 
            state = {}
            return state
      def 好处():
                 
            state = {}
            return state

      def 危害():
                 
            state = {}
            return state

      def 归属():
                 
                   
            state = {}
            return state

      def 权限():
                 
                   
            state = {}
            return state

      def 允许():
                 
                   
            state = {}
            return state

      def 禁止():
                 
                   
            state = {}
            return state

      def 标签():
            label = '人类'
            return label
      
      def 日常():
                                   
            state = {}
            return state

      def 标签():
          label = '反向人称描述'
          return label

      def 未知位置():
            state = {}
            return state

      def 确定位置():
            state = {}

            return state
                
#////////////////////////////////////////////////////////////////////
class  你们(object):
   key_person = ''
   def __init__(self):
      print("")
   def 对象(self,key_person):#
         print('测试第二人称复数')
#///////////////////////////////////////////////////////////////////////////////////////////////////
class 礼节(object):
   global usr_info
   global usr_in_word_len
   def __init__(self):
         print('礼节性字句')
   def 对象(self,key_person):#
         print('测试礼貌')

#//////////////////////////////////////////////////////////////////////////////////////////////////
class  有(object):
   global no_have_obj
   global sure_flag
   global no_flag
   global expression_three
   global answer_flag

   
   def __init__(self):
       
       print()
       
       
   def 标签():
       label = '存在'
       return label
       

#//////////////////////////////////////////////////////////////////////////////////////////////////
class  翻(object):
      
      global obj_flag
      global storage_usr_info
      #global current_key_word_obj
      global usr_in_word_len
      global mood
      global reason      
      r_parameter = ''
      def __init__(self):
          print('')
          
      def 对象(self):
          print('')
          
      def obj():
          global current_key_word_obj
          global obj_flag
          
          print('')
          
          for loc,obj_list in enumerate(mood_obj):
              print(loc,obj_list)
              if conversion_person_key_word == obj_list:
                   obj_flag = True
                   #os.system("pause")
                   break
              else:
                   if n_ksym_kperson == True:
                      obj_flag = True
                   else:
                      obj_flag = False
                                         
          print(obj_flag,conversion_person_key_word)         
          current_key_word_obj = mood_obj#注意
          print(current_key_word_obj)
          #os.system("pause")
          return obj_flag
      
      def 大纲(self):
            #er =tw
            all_dir = ['描述','行为','状态','结果','结构','用途','影响','特征','被影响'
                       ,'理由','位置','变化','过去','现在','将来','种类','必需','需要'
                       ,'理由','方法','多余','好处','危害','关系','数量'
                       ,'起源','期望','未知位置','确定位置']
            return all_dir
      
      def 描述():
                  
            state = {}
            return state

      def 行为():
            state = {}
            return state
      
      def 状态():
            describe = {}
            return describe
      
      def 结果():
            state = {}
            return state
      
      def 结构():
            state = {}
            return state
      
      def 用途():
            state = {}
            return state

      def 关系():
            state = {}
            return state

      def 起源():
                 

            state = {}
            return state
      
      def 期望():
                 

            state = {}
            return state
      
      

      def 影响():
            relevance = {}
                 
            return relevance

      def 被影响():
            state = {}
            return state
      
      def 特征():
            state = {}
            return state
      
      def 理由():
            state = {}
            return state
      
      def 位置():
            state = {}
            
            return state
      
      def 变化():
            state = {}
            return state
      
      def 需要():
                 

            state = {}
            
            return state
      def 必需():
                 
            state = {}
            return state
      
      def 方法():

            state = {}
            
            return state
      
      def 过去():
            state = {}
            return state

      def 现在():
            state = {}
            return state

      def 将来():
            state = {}
            return state

      def 种类():
            state = {}
            return state

      def 数量():
            state = {}
            return state

      def 多余():
                 
            state = {}
            return state
      def 好处():
                 
            state = {}
            return state

      def 危害():
                 
            state = {}
            return state

      def 归属():
                 
                   
            state = {}
            return state

      def 权限():
                 
                   
            state = {}
            return state

      def 允许():
                 
                   
            state = {}
            return state

      def 禁止():
                 
                   
            state = {}
            return state

      def 标签():
            label = '翻'
            return label


      def 未知位置():
            state = {}
            return state

      def 确定位置():
            state = {}

            return state
      
                  
#//////////////////////////////////////////////////////////////////////////////////////////////////
class  吃(object):
      
      global obj_flag
      global storage_usr_info
      #global current_key_word_obj
      global usr_in_word_len
      global mood
      global reason      
      r_parameter = ''
      def __init__(self):
          print('')
          
                
      def obj():
          global current_key_word_obj
          global obj_flag
          
          print('')
          
          for loc,obj_list in enumerate(mood_obj):
              print(loc,obj_list)
              if conversion_person_key_word == obj_list:
                   obj_flag = True
                   #os.system("pause")
                   break
              else:
                   if n_ksym_kperson == True:
                      obj_flag = True
                   else:
                      obj_flag = False
                                         
          print(obj_flag,conversion_person_key_word)         
          current_key_word_obj = mood_obj#注意
          print(current_key_word_obj)
          #os.system("pause")
          return obj_flag
      
      def 大纲(self):
            #er =tw
            all_dir = ['描述','对象','行为','状态','结果','结构','用途','影响','特征','被影响'
                       ,'理由','位置','变化','过去','现在','将来','种类','必需','需要'
                       ,'理由','方法','多余','好处','危害','关系','数量'
                       ,'起源','期望','未知位置','确定位置']
            return all_dir

      def 对象():
                  
            state = {}
            return state 
      
      def 描述():
                  
            state = {}
            return state

      def 行为():
            state = {}
            return state
      
      def 状态():
            describe = {}
            return describe
      
      def 结果():
            state = {}
            return state
      
      def 结构():
            state = {}
            return state
      
      def 用途():
            state = {}
            return state

      def 关系():
            state = {}
            return state

      def 起源():
                 

            state = {}
            return state
      
      def 期望():
                 

            state = {}
            return state
      
      

      def 影响():
            relevance = {}
                 
            return relevance

      def 被影响():
            state = {}
            return state
      
      def 特征():
            state = {}
            return state
      
      def 理由():
            state = {}
            return state
      
      def 位置():
            state = {}
            
            return state
      
      def 变化():
            state = {}
            return state
      
      def 需要():
                 

            state = {}
            
            return state
      def 必需():
                 
            state = {}
            return state
      
      def 方法():

            state = {}
            
            return state
      
      def 过去():
            state = {}
            return state

      def 现在():
            state = {}
            return state

      def 将来():
            state = {}
            return state

      def 种类():
            state = {}
            return state

      def 数量():
            state = {'':''}
            return state

      def 多余():
                 
            state = {}
            return state
      def 好处():
                 
            state = {}
            return state

      def 危害():
                 
            state = {}
            return state

      def 归属():
                 
                   
            state = {}
            return state

      def 权限():
                 
                   
            state = {}
            return state

      def 允许():
                 
                   
            state = {}
            return state

      def 禁止():
                 
                   
            state = {}
            return state


      def 未知位置():
            state = {}
            return state

      def 确定位置():
            state = {}

            return state

      def 标签():
            label = '吃'
            return label
      
        
#//////////////////////////////////////////////////////////////////////////////////////////////////
class  饭(object):
      
      global obj_flag
      global storage_usr_info
      #global current_key_word_obj
      global usr_in_word_len
      global mood
      global reason      
      r_parameter = ''
      def __init__(self):
          print('')
          
      def 对象(self):
          print('')
          
      def obj():
          global current_key_word_obj
          global obj_flag
          
          print('')
          
          for loc,obj_list in enumerate(mood_obj):
              print(loc,obj_list)
              if conversion_person_key_word == obj_list:
                   obj_flag = True
                   #os.system("pause")
                   break
              else:
                   if n_ksym_kperson == True:
                      obj_flag = True
                   else:
                      obj_flag = False
                                         
          print(obj_flag,conversion_person_key_word)         
          current_key_word_obj = mood_obj#注意
          print(current_key_word_obj)
          #os.system("pause")
          return obj_flag
      
      def 大纲(self):
            #er =tw
            all_dir = ['描述','行为','状态','结果','结构','用途','影响','特征','被影响'
                       ,'理由','位置','变化','过去','现在','将来','种类','必需','需要'
                       ,'理由','方法','多余','好处','危害','关系','数量'
                       ,'起源','期望','未知位置','确定位置']
            return all_dir
      
      def 描述():
                  
            state = {}
            return state

      def 行为():
            state = {}
            return state
      
      def 状态():
            describe = {}
            return describe
      
      def 结果():
            state = {}
            return state
      
      def 结构():
            state = {}
            return state
      
      def 用途():
            state = {}
            return state

      def 关系():
            state = {}
            return state

      def 起源():
                 

            state = {}
            return state
      
      def 期望():
                 

            state = {}
            return state
      
      

      def 影响():
            relevance = {}
                 
            return relevance

      def 被影响():
            state = {}
            return state
      
      def 特征():
            state = {}
            return state
      
      def 理由():
            state = {}
            return state
      
      def 位置():
            state = {}
            
            return state
      
      def 变化():
            state = {}
            return state
      
      def 需要():
                 

            state = {}
            
            return state
      def 必需():
                 
            state = {}
            return state
      
      def 方法():

            state = {}
            
            return state
      
      def 过去():
            state = {}
            return state

      def 现在():
            state = {}
            return state

      def 将来():
            state = {}
            return state

      def 种类():
            state = {}
            return state

      def 数量():
            state = {}
            return state

      def 多余():
                 
            state = {}
            return state
      def 好处():
                 
            state = {}
            return state

      def 危害():
                 
            state = {}
            return state

      def 归属():
                 
                   
            state = {}
            return state

      def 权限():
                 
                   
            state = {}
            return state

      def 允许():
                 
                   
            state = {}
            return state

      def 禁止():
                 
                   
            state = {}
            return state


      def 未知位置():
            state = {}
            return state

      def 确定位置():
            state = {}

            return state

      def 标签():
            label = '饭'
            return label
      
       
#//////////////////////////////////////////////////////////////////////////////////////////////////
class  开(object):
      
      global obj_flag
      global storage_usr_info
      #global current_key_word_obj
      global usr_in_word_len
      global mood
      global reason      
      r_parameter = ''
      def __init__(self):
          print('')
          
      def 对象(self):
          print('')
          
      def obj():
          global current_key_word_obj
          global obj_flag
          
          print('')
          
          for loc,obj_list in enumerate(mood_obj):
              print(loc,obj_list)
              if conversion_person_key_word == obj_list:
                   obj_flag = True
                   #os.system("pause")
                   break
              else:
                   if n_ksym_kperson == True:
                      obj_flag = True
                   else:
                      obj_flag = False
                                         
          print(obj_flag,conversion_person_key_word)         
          current_key_word_obj = mood_obj#注意
          print(current_key_word_obj)
          #os.system("pause")
          return obj_flag
      
      def 大纲(self):
            #er =tw
            all_dir = ['描述','行为','状态','结果','结构','用途','影响','特征','被影响'
                       ,'理由','位置','变化','过去','现在','将来','种类','必需','需要'
                       ,'理由','方法','多余','好处','危害','关系','数量'
                       ,'起源','期望','未知位置','确定位置']
            return all_dir
      
      def 描述():
                  
            state = {}
            return state

      def 行为():
            state = {}
            return state
      
      def 状态():
            describe = {}
            return describe
      
      def 结果():
            state = {}
            return state
      
      def 结构():
            state = {}
            return state
      
      def 用途():
            state = {}
            return state

      def 关系():
            state = {}
            return state

      def 起源():
                 

            state = {}
            return state
      
      def 期望():
                 

            state = {}
            return state
      
      

      def 影响():
            relevance = {}
                 
            return relevance

      def 被影响():
            state = {}
            return state
      
      def 特征():
            state = {}
            return state
      
      def 理由():
            state = {}
            return state
      
      def 位置():
            state = {}
            
            return state
      
      def 变化():
            state = {}
            return state
      
      def 需要():
                 

            state = {}
            
            return state
      def 必需():
                 
            state = {}
            return state
      
      def 方法():

            state = {}
            
            return state
      
      def 过去():
            state = {}
            return state

      def 现在():
            state = {}
            return state

      def 将来():
            state = {}
            return state

      def 种类():
            state = {}
            return state

      def 数量():
            state = {}
            return state

      def 多余():
                 
            state = {}
            return state
      def 好处():
                 
            state = {}
            return state

      def 危害():
                 
            state = {}
            return state

      def 归属():
                 
                   
            state = {}
            return state

      def 权限():
                 
                   
            state = {}
            return state

      def 允许():
                 
                   
            state = {}
            return state

      def 禁止():
                 
                   
            state = {}
            return state


      def 未知位置():
            state = {}
            return state

      def 确定位置():
            state = {}

            return state
      
      def 标签(self):
          label = '开'
          return label
            
            
#//////////////////////////////////////////////////////////////////////////////////////////////////
class  快(object):
      global obj_flag
      global storage_usr_info
      #global current_key_word_obj
      global usr_in_word_len
      r_parameter = ''

      def __init__(self):
          print('')
          
      def 对象(self):
          print('')
          
      
      
      def 属性(self):
            
            r_parameter = '测试'
            
            return r_parameter
      def 标签(self):
            state = '快'

            return state
      
      
#//////////////////////////////////////////////////////////////////////////////////////////////////
class  天(object):
      global obj_flag
      global storage_usr_info
      #global current_key_word_obj
      global usr_in_word_len
      global mood
      global reason      
      r_parameter = ''
      def __init__(self):
          print('')
          
      def 对象(self):
          print('')
          
      def obj():
          global current_key_word_obj
          global obj_flag
          
          print('')
          
          for loc,obj_list in enumerate(mood_obj):
              print(loc,obj_list)
              if conversion_person_key_word == obj_list:
                   obj_flag = True
                   #os.system("pause")
                   break
              else:
                   if n_ksym_kperson == True:
                      obj_flag = True
                   else:
                      obj_flag = False
                                         
          print(obj_flag,conversion_person_key_word)         
          current_key_word_obj = mood_obj#注意
          print(current_key_word_obj)
          #os.system("pause")
          return obj_flag
      
      def 大纲(self):
            #er =tw
            all_dir = ['描述','行为','状态','结果','结构','用途','影响','特征'
                       ,'变化','过去','现在','将来','数量','理由','方法'
                       '好处','关系','起源','期望']
            return all_dir
      
      def 描述():
                  
            state = {}
            return state

      def 行为():
            state = {}
            return state
      
      def 状态():
            describe = {}
            return describe
      
      def 结果():
            state = {}
            return state
      
      def 结构():
            state = {}
            return state
      
      def 用途():
            state = {}
            return state

      def 关系():
            state = {}
            return state

      def 起源():
                 

            state = {}
            return state
      
      def 期望():
                 

            state = {}
            return state
      
      

      def 影响():
            state = {}
                 
            return state

     
      
      def 特征():
            state = {}
            return state
      
                 
            return state
      
      def 变化():
            state = {}
            return state
      
      
            state = {}
            return state
      
      def 方法():

            state = {}
            
            return state
      
      def 过去():
            state = {}
            return state

      def 现在():
            state = {}
            return state

      def 将来():
            state = {}
            return state

      def 数量():
            state = {}
            return state

      def 标签():
            label = '循环时间量'
            return label
     

            return state
      
      
#//////////////////////////////////////////////////////////////////////////////////////////////////
class  哪个(object):
      global obj_flag
      global storage_usr_info
      #global current_key_word_obj
      global usr_in_word_len
      r_parameter = ''

      def __init__(self):
          print('')
          
      def 对象(self):
          print('')
          
      def 标签():
          label = '多_选一'
          return label
#//////////////////////////////////////////////////////////////////////////////////////////////////
class 是(object):
      
      
      global first_to_five_label
      global first_to_five_list
      
      global first_kw_flag
      global key_word_list
      
      global second_kw_flag
      global second_key_word_list
      global d_class_list
      global d_okw_class_list
      global key_word_count
      
      global info_word_loc_list
      global key_word_list_content

      def __init__(self):
          print('询问属性或内容')
     
      def 标签():

         label = '属性描述'
         return label

#///////////////////////////////////////////////////////////////////////////////////////////////////
class 哪里(object):
      
      
      global first_to_five_label
      global first_to_five_list
      
      global first_kw_flag
      global key_word_list
      
      global second_kw_flag
      global second_key_word_list
      global d_class_list
      global d_okw_class_list
      global key_word_count
      
      global info_word_loc_list
      global key_word_list_content

      def __init__(self):
          print('询问属性或内容')
     
      def 标签():

         label = '未知位置'
         return label

#///////////////////////////////////////////////////////////////////////////////////////////////////

class 还是(object):
      
      
      global first_to_five_label
      global first_to_five_list
      
      global first_kw_flag
      global key_word_list
      
      global second_kw_flag
      global second_key_word_list
      global d_class_list
      global d_okw_class_list
      global key_word_count
      
      global info_word_loc_list
      global key_word_list_content

      def __init__(self):
          print('询问属性或内容')
     
      def 标签():

         label = '不确定属性描述'
         #os.system("pause")#
         return label
      
#//////////////////////////////////////////////////////////////////////////////////////////////////
class  没有(object):
      global obj_flag
      global storage_usr_info
      #global current_key_word_obj
      global usr_in_word_len
      r_parameter = ''

      def __init__(self):
          print('')
          
      def 标签():
          label = '不存在'
          return label
#//////////////////////////////////////////////////////////////////////////////////////////////////
class  有没有(object):
   global no_have_obj
   global sure_flag
   global no_flag
   global expression_foru
   global answer_flag
   
   none = '没有 '
   have = '有 '
   cause = ''
   add_info = ''
   
   def __init__(self):
       
       print('')
       
   
#/////////////////////////////////////////////////////////////////////////////////////////////////
class 损坏(object):      

      
      global obj_flag
      global storage_usr_info
      #global current_key_word_obj
      global usr_in_word_len
      global mood
      global reason      
      r_parameter = ''
      def __init__(self):
          print('')
          
      def 对象(self):
          print('')
          
      
      def 探测(self):
            c_name = ''
            return c_name
      
      def 属性(self):
            r_parameter = ''
            return r_parameter
      def 状态(self):
            state = {}
            return state
      
      def 查询(self):
            state = {}
            return state
      
      def 特性(self):
            relevance = []
            global reason
            if reason == 0:
               exam = 1
               reason = 1
               
            elif reason == 1:
                 exam = 2
                 reason = 2
                 
            elif reason == 2:
                 exam = 3
                 reason = 3
                 
            return reason,relevance
#/////////////////////////////////////////////////////////////////////////////////////////////////

#///////////////////////////////////////////////////////////////////////////////////////////////////
class 少(object):
      global storage_usr_info
      #global current_key_word_obj
      global usr_in_word_len
      r_parameter = ''

      def __init__(self):
          print('')
          
      def 对象(self):
          print('')
          
      
      
      def 大纲(self):
            #er =tw
            all_dir = ['描述']
            return all_dir
      
      def 描述():
                  
            state = {}
            return state

      def 标签():

            label = '数量描述'
            
            return label
      
      
#//////////////////////////////////////////////////////////////////////////////////////////////////
class 多少(object):
      global obj_flag
      global storage_usr_info
      #global current_key_word_obj
      global usr_in_word_len
      r_parameter = ''

      def __init__(self):
          print('')
          
      def 对象(self):
          print('')
          
      
      
      def 大纲(self):
            #er =tw
            all_dir = ['描述']
            return all_dir
      
      def 描述():
                  
            state = {}
            return state

      def 标签():
            label = '未知数字'
            return label
      
      
#//////////////////////////////////////////////////////////////////////////////////////////////////
class 次(object):
      global obj_flag
      global storage_usr_info
      #global current_key_word_obj
      global usr_in_word_len
      r_parameter = ''

      def __init__(self):
          print('')
          
      def 对象(self):
          print('')
          
      
      
      def 大纲(self):
            #er =tw
            all_dir = ['描述']
            return all_dir
      
      def 描述():
                  
            state = {}
            return state

      def 标签():
            label = '数量单位'
            return label
      
      
#//////////////////////////////////////////////////////////////////////////////////////////////////
class 年龄(object):
     
      
      global obj_flag
      global storage_usr_info
      #global current_key_word_obj
      global usr_in_word_len
      global mood
      global reason      
      r_parameter = ''
      def __init__(self):
          print('')
          
      def 对象(self):
          print('')
          
      def obj():
          global current_key_word_obj
          global obj_flag
          
          print('')
          
          for loc,obj_list in enumerate(mood_obj):
              print(loc,obj_list)
              if conversion_person_key_word == obj_list:
                   obj_flag = True
                   #os.system("pause")
                   break
              else:
                   if n_ksym_kperson == True:
                      obj_flag = True
                   else:
                      obj_flag = False
                                         
          print(obj_flag,conversion_person_key_word)         
          current_key_word_obj = mood_obj#注意
          print(current_key_word_obj)
          #os.system("pause")
          return obj_flag
      
      def 大纲(self):
            #er =tw
            all_dir = ['描述','行为','状态','结果','结构','用途','影响','特征','被影响'
                       ,'理由','位置','变化','过去','现在','将来','种类','必需','需要'
                       ,'理由','方法','多余','好处','危害','关系'
                       ,'起源','期望','未知位置','确定位置']
            return all_dir
      
      def 描述():
                 
            state = {}
            return state

      def 行为():
            state = {}
            return state
      
      def 状态():
            describe = {}
            return describe
      
      def 结果():
            state = {}
            return state
      
      def 结构():
            state = {}
            return state
      
      def 用途():
            state = {}
            return state

      def 关系():
            state = {}
            return state

      def 起源():
                 

            state = {}
            return state
      
      def 期望():
                 

            state = {}
            return state
      
      

      def 影响():
            relevance ={}
                 
            return relevance

      def 被影响():
            state = {}
            return state
      
      def 特征():
            state = {}
            return state
      
      def 理由():
            state = {}
            return state
      def 位置():
            state = {}
            return state
      
      def 变化():
            state = {}
            return state
      
      def 需要():
                 

            state = {}
            return state
      def 必需():
                 
 
            state = {}
            return state
      
      def 方法():

            state = {}
            return state
      
      def 过去():
            state = {}
            return state

      def 现在():
            state = {}
            return state

      def 将来():
            state = {}
            return state

      def 种类():
            state = {}
            return state

      def 多余():
                 
            state = {}
            return state
      def 好处():
                 
            state = {}
            return state

      def 危害():
                 
            state = {}
            return state

      def 归属():
                 
                   
            state = {}
            return state

      def 权限():
                 
                   
            state = {}
            return state

      def 允许():
                 
                   
            state = {}
            return state

      def 禁止():
                 
                   
            state = {}
            return state


      def 未知位置():
            state = {}
            return state

      def 确定位置():
            state = {}
            return state 
#//////////////////////////////////////////////////////////////////////////////////////////////////

#//////////////////////////////////////////////////////////////////////////////////////////////////

#//////////////////////////////////////////////////////////////////////////////////////////////////
class 钱(object):
            
      global obj_flag
      global storage_usr_info
      #global current_key_word_obj
      global usr_in_word_len
      global mood
      global reason
      
      r_parameter = ''

      def __init__(self):
          print('')
          
      def 对象(self):
          print('')
          
      
      
      def 大纲(self):
            #er =tw
            all_dir = ['描述','行为','状态','结果','结构','用途','影响','特征','被影响'
                       ,'理由','位置','变化','过去','现在','将来','种类','必需','需要'
                       ,'理由','方法','多余','好处','危害','关系'
                       ,'起源','期望','数量','未知位置','确定位置']
            return all_dir
      
      def 描述():
                 
          state = {''}
          return state

      def 行为():
            state = {}
            return state
      
      def 状态():
          state = {''}
          return state
      
      def 结果():
            state = {}
            return state
      
      def 结构():
          state = {''}
          return state
      
      def 用途():
          state = {''}
          return state

      def 关系():
          state = {''}
          return state

      def 起源():
                 
          state = {''}
          return state
      
      def 期望():
                 
          state = {''}
          return state
      

      def 影响():
          state = {''}
          return state

      def 被影响():
          state = {''}
          return state
      
      def 特征():
          state = {''}
          return state
      
      def 理由():
          state = {''}
          return state
      
      def 位置():
          state = {''}
          return state
      
      def 变化():
          state = {''}
          return state
      
      def 需要():
                 
          state = {''}
          return state
      
      def 必需():
                 
          state = {''}
          return state
      
      def 方法():

          state = {''}
          return state

      
      def 过去():
          state = {''}
          return state

      def 现在():
          state = {''}
          return state

      def 将来():
           state = {''}
           return state

      def 种类():
          state = {''}
          return state
                 
          state = {''}
          return state
      def 好处():
          state = {''}
          return state

      def 危害():
                 
          state = {''}
          return state

      def 归属():
                 
          state = {''}
          return state

      def 权限():
                 
          state = {''}
          return state
      
      def 允许():
                 
                   
          state = {''}
          return state

      def 禁止():
                 
                   
          state = {''}
          return state

      def 数量():
            state = {}
            return state

      def 标签():
            label = '钱'
            return label


      def 未知位置():
            state = {''}
            return state

      def 确定位置():
            state = {''}
            return state

#//////////////////////////////////////////////////////////////////////////////////////////////////

#//////////////////////////////////////////////////////////////////////////////////////////////
class 怎么(object):
      
      def __init__(self):
            print('询问原因或状态')
    

      def 标签():
          label = '原因_结果询问'
          return label
            
#///////////////////////////////////////////////////////////////////
class 就(object):      
      
      def __init__(self):
          print('')
            

      
      global first_to_five_label
      global first_to_five_list
      
      global first_kw_flag
      global key_word_list
      
      global second_kw_flag
      global second_key_word_list
      global d_class_list
      global d_okw_class_list
      global key_word_count
      
      global info_word_loc_list
      global key_word_list_content

      def 标签():

         label = '就'
         return label
#////////////////////////////////////////////////////////////////////////////////////////////////////
class 获得(object):      
      
      def __init__(self):
          print('')                     

      def 标签():

         label = '所有权描述'
         return label
#////////////////////////////////////////////////////////////////////////////////////////////////////
class 如何(object):      
      
      def __init__(self):
          print('询问原因')      
      
      def 标签():

         label = '询问方法'
         return label
#//////////////////////////////////////////////////////////////////////////////////////////////////
class 好(object):      
      
      def __init__(self):
          print('询问原因')                       

      def 标签():

          label = '好'
          return label      
#//////////////////////////////////////////////////////////////////////////////////////////////////
class 为什么(object):      
      
      def __init__(self):
            print('询问原因')

      def 标签():
          label = '询问原因'
          return label
          
#//////////////////////////////////////////////////////////////////
class 什么(object):
      

      def __init__(self):
          print('')
     
      def 标签():

         label = '属性_内容询问'
         return label
#/////////////////////////////////////////////////////////////////////////////////////////////////////
class 男性(object):
      

      def __init__(self):
          print('询问属性或内容')
     
      def 标签():

         label = '性别'
         return label
#///////////////////////////////////////////////////////////////////////////////////////////////////
class 女性(object):
      

      def __init__(self):
          print('询问属性或内容')
     
      def 标签():

         label = '性别'
         return label     
#///////////////////////////////////////////////////////////////////////////////////////////////////
class 儿童(object):
      

      def __init__(self):
          print('询问属性或内容')
     
      def 标签():

         label = '儿童'
         return label
#///////////////////////////////////////////////////////////////////////////////////////////////////
class 婴儿(object):
      

      def __init__(self):
          print('询问属性或内容')
     
      def 标签():

         label = '婴儿'
         return label      
#///////////////////////////////////////////////////////////////////////////////////////////////////
class 今天(object):
      
       def __init__(self):
            print('时间')
            
       def 对象(self):

            print('今天->>>时间对象看这里')
            
       def obj():
          global obj_flag
          global current_key_word_obj
          time_flag = True
          obj_flag  = True
          print('时间标记位:',time_flag)
          return obj_flag
#/////////////////////////////////////////////////////////////////////////////////////////////////
class 多(object):
      

      def __init__(self):
          print('')
          
      def 对象(self):
          print('')
          
      
      
      def 大纲(self):
            #er =tw
            all_dir = ['描述']
            return all_dir
      
      def 描述():
                  
            state = {}
            return state

      def 标签():

            label = '数量描述'
             
            return label
#--------------------------------------------------------------------------------------------------
def acquire_resule(t_obj,ref_sub_kw,before_wd_add_list,after_wd_add_list):
      
    global map_table
    global map_flag
    global f_result_flag
    global ignore_key_word_list
    r_value_flag = False
    seer_array = ''
    a_r_map_obj = '' 
    a_t_obj = ''
    a_gc_obj = ''
    a_ref_sub_kw = ''
    a_before_wd_add_list = ''
    a_after_wd_add_list = ''
    a_back_wd = ''
    a_back_wd_list = []
    t_wd_list = []
    t_loc = 0
    t_wd_len = 0
    a_t_obj = t_obj
    a_ref_sub_kw = ref_sub_kw
    a_before_wd_add_list = before_wd_add_list
    a_after_wd_add_list = after_wd_add_list
    #a_back_wd = back_wd f_result_flag = True
    
#--------------------------------------------------------------------------------------------------
    r_value_flag = hasattr(eval(a_t_obj),a_ref_sub_kw)        
    if r_value_flag:           
           print('✔✔✔✔对象存在对应子项:',a_ref_sub_kw)    
           seer_array =  getattr(eval(a_t_obj)(),a_ref_sub_kw)(a_before_wd_add_list)
           
           #print('☁☁☁☁获取答案:',seer_array)
           if seer_array == False:
              print('✘✘✘✘相应对象子项找不到答案✘✘✘✘:',seer_array)                         

              seer_array =  getattr(eval(a_t_obj)(),a_ref_sub_kw)(a_after_wd_add_list)
           #print('☁☁☁☁获取答案:',seer_array)
              if seer_array == False:
                 print('✘✘✘✘相应对象子项找不到答案✘✘✘✘:',seer_array)

                 a_back_wd = (a_before_wd_add_list + a_after_wd_add_list)
                 seer_array =  getattr(eval(a_t_obj)(),a_ref_sub_kw)(a_back_wd)
           
           #print('☁☁☁☁获取答案:',seer_array)
                 if seer_array == False:
                    print('✘✘✘✘相应对象子项找不到答案✘✘✘✘:',seer_array)
                    
           else:
               f_result_flag = True
               #print('☁☁☁☁获取答案:',seer_array)
#启动映射查询-对象及查询关键元素---------------------------------------------------------------------------------------                         
           if f_result_flag == False:   
              #gc_back_wd = back_wd #传递值给全局变量
              a_gc_obj = a_t_obj #传递值给全局变量
              print('☂☂☂☂启动映射查询:',a_t_obj)
              a_r_map_obj = map_check(a_gc_obj)
              if map_flag:
                 a_t_obj = a_r_map_obj
                 map_flag = False
                 a_gc_obj = a_t_obj
                 print('✿✿✿✿映射成功--更新对象',a_t_obj)
#更新对象后重新查询答案-----------------------------------------------------------------------------                 
              r_value_flag = hasattr(eval(a_t_obj),a_ref_sub_kw)
              if r_value_flag:
                 print('✔✔✔✔对象存在对应子项:',a_ref_sub_kw)    
                 seer_array =  getattr(eval(a_t_obj)(),a_ref_sub_kw)(a_before_wd_add_list)
                 #print('☁☁☁☁获取答案:',seer_array)
                 if seer_array == False:
                    print('✘✘✘✘相应对象子项找不到答案✘✘✘✘:',seer_array)


                    seer_array =  getattr(eval(a_t_obj)(),a_ref_sub_kw)(a_after_wd_add_list)
                    #print('☁☁☁☁获取答案:',seer_array)
                    if seer_array == False:
                       print('✘✘✘✘相应对象子项找不到答案✘✘✘✘:',seer_array)


                       a_back_wd = a_before_wd_add_list + a_after_wd_add_list
                       seer_array =  getattr(eval(a_t_obj)(),a_ref_sub_kw)(a_back_wd)
                       #print('☁☁☁☁获取答案:',seer_array)
                       if seer_array == False:
                          print('✘✘✘✘相应对象子项找不到答案✘✘✘✘:',seer_array)
                 else:
                     f_result_flag = True
                     #print('☁☁☁☁获取答案:',seer_array)
#--------------------------------------------------------------------------------------------------
           if f_result_flag == False:
                 
              #gc_back_wd = back_wd #传递值给全局变量
              #a_gc_obj = a_t_obj #传递值给全局变量
              print('〄〄〄〄再次启动映射查询:',a_back_wd)

              if ignore_key_word_list:
                 
                 for icc,ikk in enumerate(ignore_key_word_list):
                     if ikk in a_back_wd:
                                
                        t_loc = a_back_wd.find(ikk)
                        t_wd_len = len(ikk)
                        #usr_info = usr_info[0:t_key_pw_loc]+usr_info[t_key_pw_loc+t_key_pw_len:]
                        a_back_wd = a_back_wd[0:t_loc] + a_back_wd[t_loc + t_wd_len:]
                        print('这里',a_back_wd)
                 print('☛☛☛☛更新对应元素',a_back_wd)
              a_r_map_obj = map_check(a_back_wd)
              if map_flag:
                 a_t_obj = a_r_map_obj
                 map_flag = False
                 print('✿✿✿✿映射成功--更新元素',a_t_obj,a_t_obj,a_ref_sub_kw)


    r_value_flag = hasattr(eval(a_gc_obj),a_ref_sub_kw)
    if r_value_flag:
       print('✔✔✔✔对象存在对应子项:',a_ref_sub_kw)    
       seer_array =  getattr(eval(a_gc_obj)(),a_ref_sub_kw)(a_t_obj)
       #print('☁☁☁☁获取答案:',seer_array)
       if seer_array == False:
          print('✘✘✘✘相应对象子项找不到答案✘✘✘✘:',seer_array)

       else:
           f_result_flag = True
        
          
#--------------------------------------------------------------------------------------------------
    if f_result_flag:
       print('☃☃☃☃成功',seer_array)  
       return seer_array
      
    else:
       print('▓▓▓▓失败',f_result_flag)   
       return f_result_flag
#-------------------------------------------------------------------------------------------------- 
def map_check(obj):
    global map_table
    global map_flag
    type_judge = False
    type_value = False

    check_kw = ''
    t_obj = ''
    t_key_check_wd = ''

    t_obj = obj
    #check_kw = find_kw
    #back_wd = key_check_wd
    print('♨♨♨♨准备分析映射❉❉❉❉')
#--------------------------------------------------------------------------------------------------
    for mc,mk in map_table.items():
                  type_judge = isinstance(mc, str)                    
                  
                  if type_judge:
                     print('字符')
                     
                     if mc == t_obj: #t_obj
                        print('匹配',mc)   
                        map_flag = True

                        type_value = isinstance(mk, str)   
                        if type_value:
                              
                           back_wd = mk#直接取代当前对象
                           print('☛☛☛☛字符-找到对象映射字符-键:',t_obj)
                           
                        else:
                            t_obj = mk[0]#直接取第一个元素取代当前对象   
   
                            print('☛☛☛☛找到对象映射-字符值:',t_obj)
                            
                     else:

                         type_value = isinstance(mk, str)   
                         if type_value:  
                            if mk == t_obj:
 
                                map_flag = True     
                                t_obj = mc#直接取代当前对象
                                print('☛☛☛☛字符值找到对象映射-字符键:',t_obj)
                                #else:
                                    #t_obj = mk[0]#直接取第一个元素取代当前对象   
                                     
                                    #print('☛☛☛☛字符-找到对象映射字符-值:',t_obj)
                         else:
                               for fc,fk in enumerate(mk):
                                   if fk == t_obj:
   
                                      map_flag = True
                                      t_obj = mc
                                      print('☛☛☛☛字符值找到对象映射-元祖键:',t_obj)
                     
                  else:
                        
                     for tic,tjk in enumerate(mc):
                         print('键元祖')
                         
                         if tjk == t_obj:
                               
                            type_value = isinstance(mk, str)   
                            if type_value:
   
                               map_flag = True   
                               t_obj = mk#直接取代当前对象
                               print('☛☛☛☛元祖键-找到对象映射-字符值:',t_obj)
                               
                            else:
                                t_obj = mk[0]#直接取第一个元素取代当前对象   
                                map_flag = True   
                                print('☛☛☛☛元祖键-找到对象映射-元祖值:',t_obj)
                                
                     if map_flag == False:#元祖值和元组键查询
                           
                        for tic,tjk in enumerate(mk):
                            print('值元祖')
                         
                            if tjk == t_obj:

                               #type_value = isinstance(mk, str)   
                               #if type_value:
                               map_flag = True   
                               t_obj = mc[0]#直接取第一个元素取代当前对象
                               print('☛☛☛☛元祖键-找到对象映射-字符值:',t_obj)
                               
    return t_obj
#--------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------- ---               
          
#/////////////////////////////////////////////////////////////////////////////////////////////////      
how_do_flag   = False

tone_flag     = False
le_flag       = False
polite_flag   = False
de_flag       = False

k_symbol_flag = False

have_obj       = ''
none_have      = ''
no_have_obj    = ''

quantity_flag  = False
very_flag      = False
poor_flag      = False
skill_flag     = False
much_flag      = False
few_flag       = False
fast_flag      = False
s_tur          = False

s_which        = False
open_flag      = False
chi_flag       = False
ci_flag        = False
ds_flag        = False
day_flag       = False
open_flag      = False
sleep_flag     = False
body_flag      = False
health_flag    = False
bi_flag        = False
big_flag       = False
how_flag       = False

k_symbol_flag  = False #关键符号标志

in_word_len    = 0

#/////////////////////////////////////////////////////////////////////

#/////////////////////////////////////////////////////////////////////
                 

#以下是字典/关键字匹配定义///////////////////////////////////////////////////////////////////
d_person   =  {'你':你()}#
d_persons  =  {'你们':你们()}
d_sperson  =  {'我':我}
#d_spersons  = {'我们':我们}

s_person   =  {'你':you_flag}#
s_persons  =  {'你们':your_flag}
s_sperson  =  {'你':i_flag}

d_miss     =  {'思念':思念}
d_smiss    =  {'想念':思念}
d_tmiss    =  {'怀念':思念}
d_fmiss    =  {'牵挂':思念}


d_money   =  {'钱'  :钱}#

d_talk    =  {'说':说}
d_stalk   =  {'讲':说}
d_ttalk   =  {'说话':说}
d_ftalk   =  {'讲话':说}

d_get     =  {'给':给}
d_sget    =  {'拿给':给}
d_tget    =  {'给予':给}

s_gei     =  {'给':get_flag}
s_sgei    =  {'拿给':get_flag}
s_tgei    =  {'给予':get_flag}

s_talk    =  {'说':talk_flag}
s_stalk   =  {'讲':talk_flag}
s_ttalk   =  {'说话':talk_flag}
s_ftalk   =  {'讲话':talk_flag}

d_story   =  {'故事':故事} 
d_sstory  =  {'往事':故事}

s_story   =  {'故事':story_flag}
s_sstory  =  {'往事':story_flag}

d_humor   =  {'笑话':幽默}
d_shumor  =  {'幽默':幽默}
s_humor   =  {'幽默':humor_flag}
s_shumor  =  {'笑话':humor_flag}

d_mood    =  {'心情':心情}
d_smood   =  {'情绪':心情}
s_smood   =  {'情绪':mood_flag}
s_mood    =  {'心情':mood_flag}

d_play    =  {'玩':玩乐}
d_buy     =  {'买':买}

d_splay   =  {'玩得':玩乐}
d_tplay   =  {'玩耍':玩乐}
d_fplay   =  {'好玩':玩乐}
d_nplay   =  {'不好玩':玩乐}
s_play    =  {'玩':play_flag}

d_exam    =  {'考试':考试}
d_sexam    = {'考得':考试}

d_texam    = {'测试':考试}
d_examf    = {'考核':考试}
d_fexam    = {'考':考试}

d_appe_wk  = {'胃口':胃口}

d_ahappy =   {'兴奋':开心}
d_bhappy =   {'高兴':开心}
d_chappy  =  {'开心':开心}
d_dhappy =   {'笑':开心}
d_ehappy =   {'大笑':开心}
d_fhappy =   {'哈哈大笑':开心}
d_ghappy  =  {'哈哈':开心}
d_hhappy =   {'呵呵':开心}
d_ihappy =   {'激动':开心}
#d_jhappy =   {'心情很好':开心}

s_ahappy =   {'兴奋':happy_flag}
s_bhappy =   {'高兴':happy_flag}
s_chappy  =  {'开心':happy_flag}
s_dhappy =   {'笑':happy_flag}
s_ehappy =   {'大笑':happy_flag}
s_fhappy =   {'哈哈大笑':happy_flag}
s_ghappy =   {'哈哈':happy_flag}
s_hhappy =   {'呵呵':happy_flag}
s_ihappy =   {'激动':happy_flag}
#s_jhappy =   {'心情很好':happy_flag}
#-------------------------------------------------------------------------------------------------
d_asad =   {'郁闷':难过}
d_bsad =   {'忧愁':难过}
d_csad =   {'伤心':难过}
d_dsad =   {'难过':难过}
d_esad =   {'大笑':难过}
d_fsad =   {'悲哀':难过}
d_gsad =   {'哭泣':难过}
d_hsad =   {'悲伤':难过}
d_isad =   {'不开心':难过}


s_asad =   {'郁闷':sad_flag}
s_bsad =   {'忧愁':sad_flag}
s_csad =   {'伤心':sad_flag}
s_dsad =   {'难过':sad_flag}
s_esad =   {'大笑':sad_flag}
s_fsad =   {'悲哀':sad_flag}
s_gsad =   {'哭泣':sad_flag}
s_hsad =   {'悲伤':sad_flag}
s_isad =   {'不开心':sad_flag}


d_call     = {'名字':名字}
d_scall    = {'姓名':名字}
d_tcall    = {'称呼':名字}
d_fcall    = {'小名':名字}
d_ycall    = {'英文名':名字}
d_xcall    = {'叫':叫}

d_differen = {'区别':区别}
d_sdifferen= {'差异':区别}
d_tdifferen = {'不同':区别}

s_differen = {'区别':dif_flag}
s_sdifferen= {'差异':dif_flag}
s_tdifferen = {'不同':dif_flag}

s_call     = {'名字':call_flag}
s_scall    = {'姓名':call_flag}
s_tcall    = {'称呼':call_flag}
s_fcall    = {'小名':call_flag}
s_ycall    = {'英文名':call_flag}
s_xcall    = {'叫':jiao_flag}

d_age     =  {'年龄':年龄}
d_how_old =  {'多大':年龄}
d_how_age =  {'几岁':年龄}

d_poor     = {'不好':不好}
d_zaogao   = {'糟糕':不好}
d_cj       = {'差劲':不好}
d_hc       = {'差':不好}

d_can      = {'能':能}#

d_tcan     = {'可以':可以}
d_meet     = {'会':会}#


d_enough   = {'足够':足够}
d_senough  = {'足够多':足够}
d_tenough  = {'充足':足够}
d_keep     = {'维持':维持}
d_skeep    = {'维护':维持}


d_help     = {'帮':协助}#
d_shelp    = {'帮忙':协助}
d_thelp    = {'帮助':协助}
d_thelp    = {'协助':协助}
d_cn       = {'才能':才能}

s_meet      = {'会':meet_flag}
s_can      = {'能':can_flag}
s_tcan     = {'可以':may_flag}
s_cn       = {'才能':cn_flag}

s_enough   = {'足够':enough_flag}
s_senough  = {'足够多':enough_flag}
s_tenough  = {'充足':enough_flag}
s_keep     = {'维持':keep_flag}
s_skeep    = {'维护':keep_flag}

s_help     = {'协助':help_flag}
s_shelp    = {'帮助':help_flag}
s_thelp    = {'帮忙':help_flag}
s_fhelp    = {'帮':help_flag}

d_and       = {'和平':和平}
s_and       = {'和平':peace_flag}



#d_th       = {'想':c_kw_flag}
#d_sth      = {'要':c_kw_flag}

s_get     =  {'把':get_flag}
s_to      =  {'把':to_flag}

#d_tth      = {'希望':c_kw_flag}
#d_fth      = {'期望':c_kw_flag}

d_what    =  {'什么':什么}

d_why     =  {'为什么':为什么}
d_whyh    =  {'为何':为什么}
d_whys    =  {'为啥':为什么}

s_why     =  {'为什么':why_flag}
s_whyh    =  {'为何':why_flag}
s_whys    =  {'为啥':why_flag}

d_how     =  {'怎么':怎么}
s_how     =  {'怎么':how_flag}
d_tone    =  {'吗'  :tone_flag}
s_le      =  {'了'  :le_flag}
              
s_polite  =  {'请问':polite_flag}
s_de      =  {'的':de_flag}

d_need    =  {'需要':需要}
d_sneed   =  {'必需':需要}   

d_snone   =  {'没':没有}
d_none    =  {'没有':没有}
d_have_none = {'有没有':have_none_flag}
d_have    =  {'有':有}

s_snone   =  {'没':none_flag}
s_none    =  {'没有':none_flag}
s_have_none = {'有没有':have_none_flag}
s_have    =  {'有':have_flag}

d_how_much = {'多少':quantity_flag}

d_much      = {'多':多}
d_smuch     = {'很多':多}
d_tmuch     = {'非常多':多}
d_fmuch     = {'更多':多}

d_few       = {'少':少}
d_sfew      = {'很少':少}
d_tfew      = {'非常少':少}
d_ffew      = {'更少':少}

s_very     = {'很':  very_flag}
s_svery    = {'非常':  very_flag}

d_quantity = {'数量':quantity_flag}
d_how_far =  {'多远':quantity_flag}
d_how_hight ={'多高':quantity_flag}
d_how_near  ={'多近':quantity_flag}
d_how_short ={'多矮':quantity_flag}

d_hight    = {'身高':高度}
d_shight   = {'高度':高度}

s_hight    = {'身高':hight_flag}
s_shight   = {'高度':hight_flag}

d_sp         = {'东西':东西}
d_ssp        = {'商品':东西}
d_tsp        = {'物品':东西}

d_pc         = {'电脑':电脑}
d_spc        = {'计算机':电脑}

d_code       = {'代码':代码}
d_scode      = {'编码':代码}

s_code       = {'代码':code_flag}
s_scode      = {'编码':code_flag}

d_rl        = {'人类':人类}
d_r         = {'人':人类}

d_sleep     = {'睡眠':睡眠}
d_ssleep    = {'睡觉':睡眠}
d_tsleep    = {'睡着':睡眠}
d_fsleep    = {'睡':睡眠}

d_health    = {'健康':健康}
d_shealth   = {'安康':健康}
d_thealth   = {'平安':健康}
d_fhealth   = {'没事':健康}


d_body      = {'身体':身体}
d_sbody     = {'身躯':身体}
d_tbody     = {'身子':身体}
d_fbody     = {'身':身体}

d_jloc      = {'家':家}
d_jlloc     = {'家里':家}
ds_hjloc    = {'回家':家}
ds_zjlloc   = {'在家里':家}

d_fan       = {'饭':饭}
d_sfan      = {'米饭':饭}

d_water     = {'水':水}
d_dwater    = {'淡水':水}
d_xwater    = {'咸水':水}
d_zlwater   = {'自来水':水}

d_food      = {'食物':食物}
d_sfood     = {'食品':食物}

d_air       = {'空气':空气}

d_sun       = {'太阳':太阳}
d_moon      = {'月亮':月亮}
d_bi        = {'比':比}


d_zfire      = {'着火':火}
d_qfire      = {'起火':火}
d_sfire      = {'火烧':火}
d_wfire      = {'火灾':火}
d_fire       = {'火':火}

d_car       = {'车':车}
d_qcar      = {'汽车':车}
d_ship      = {'轮船':船}
d_lship     = {'船':船}

d_ap        = {'飞机':飞机}

d_open      = {'开':开}
d_sopen     = {'打开':开}

d_chi       =  {'吃':吃}
d_ci        =  {'次':次}
d_dun       =  {'顿':次}
d_ds        =  {'几':多少}
d_day       =  {'天':天}
d_mt        =  {'每天':天}
d_yt        =  {'一天':天}

d_tur       =  {'翻倒':翻}
d_stur      =  {'侧翻':翻}
d_ttur      =  {'翻开':翻}
d_ftur      =  {'翻':翻}

d_small      =  {'小':小}
d_big        =  {'大':大}
d_tk         =  {'太快':快}
d_gk         =  {'更快':快}
d_hk         =  {'很快':快}
d_fck        =  {'非常快':快}
d_k          =  {'快':快}

d_which      =  {'哪个':哪个}
d_swhich     =  {'哪一个':哪个}
d_who        =  {'谁':谁}
s_who        =  {'谁':who_flag}

d_rh         =  {'如何':如何}
d_srh        =  {'怎样':如何}
d_trh        =  {'怎么样':如何}
d_frh        =  {'怎么做':如何}


d_hd        =  {'获得':获得}
d_sh        =  {'收获':获得}
d_dd        =  {'得到':获得}
d_hq        =  {'获取':获得}
d_yy        =  {'拥有':获得}
d_qd        =  {'取得':获得}

d_exit      =  {'住在':存在}
d_sexit     =  {'在':存在}


s_exit      =  {'住在':exit_flag}
s_sexit     =  {'在':exit_flag}

d_result    =  {'结果':结果}
d_sresult   =  {'后果':结果}
d_tresult   =  {'结局':结果}

d_is        =  {'是':是}
s_is        =  {'是':is_flag}

d_hs        =  {'还是':还是}
s_hs        =  {'还是':or_flag}      

d_man       =  {'男性':男性}
d_sman      =  {'男人':男性}
d_tman      =  {'男生':男性}
d_fman      =  {'男子':男性}
d_xman      =  {'雄性':男性}

d_wm        =  {'女性':女性}
d_swm       =  {'女人':女性}
d_twm       =  {'女生':女性}
d_fwm       =  {'女子':女性}
d_xwm       =  {'雌性':女性}

d_ge        =  {'个':个}
s_ge        =  {'个':ge_flag}

s_man       =  {'男性':man_flag}
s_sman      =  {'男人':man_flag}
s_tman      =  {'男生':man_flag}
s_fman      =  {'男子':man_flag}
d_xman      =  {'雄性':man_flag}

s_wm        =  {'女性':wm_flag}
s_swm       =  {'女人':wm_flag}
s_twm       =  {'女生':wm_flag}
s_fwm       =  {'女子':wm_flag}
d_xwm       =  {'雌性':wm_flag}

d_child     =  {'儿童':儿童}
d_schild    =  {'小孩':儿童}

s_child     =  {'儿童':child_flag}
s_schild    =  {'小孩':child_flag}

d_baby      =  {'婴儿':baby_flag}
s_baby      =  {'宝宝':baby_flag}

d_product   =  {'产品':产品}
s_product   =  {'产品':product_flag}

d_create    =  {'创造':创造}
d_screate   =  {'制造':创造}
d_tcreate   =  {'设计':创造}
d_fcreate   =  {'生产':创造}

d_mission   =  {'使命':使命}
d_smission  =  {'任务':使命}
d_tmission  =  {'目标':使命}
d_fmission  =  {'目的':使命}

s_mission   =  {'使命':miss_flag}
s_smission  =  {'任务':miss_flag}
s_tmission  =  {'目标':miss_flag}
s_fmission  =  {'目的':miss_flag}

s_create    =  {'创造':create_flag}
s_screate   =  {'制造':create_flag}
s_tcreate   =  {'设计':create_flag}
s_fcreate   =  {'生产':create_flag}

d_now       =  {'现在':现在}
d_snow      =  {'目前':现在}

s_now       =  {'现在':now_flag}
s_snow      =  {'目前':now_flag}

d_use       =  {'用':用}
d_suse       =  {'使用':用}

s_use       =  {'用':use_flag}
s_suse      =  {'使用':use_flag}

d_oc       =   {'只能':只能}
d_soc      =   {'只会':只能}     
d_toc      =   {'只可以':只能}   

s_oc       =   {'只能':oc_flag}
s_soc      =   {'只会':oc_flag}
s_toc      =   {'只可以':oc_flag}

d_txt      =   {'文字':文字}
#d_stxt     =   {'故事':文字}
#d_tstxt    =   {'笑话':文字}
s_txt      =   {'文字':txt_flag}
#s_stxt     =   {'故事':txt_flag}
#s_ttxt     =   {'笑话':txt_flag}

d_gt       =   {'沟通':沟通}
d_jl       =   {'交流':沟通}

s_gt       =   {'沟通':gt_flag}
s_jl       =   {'交流':gt_flag}

d_or       =   {'和':和}
d_sor      =   {'以及':和}
d_tor      =   {'还有':和}

s_or       =   {'和':he_flag}
s_sor      =   {'以及':he_flag}
s_tor      =   {'还有':he_flag}
#-------------------------------------------------------------------------------------------------
d_skill    =   {'技术':技能}
d_sskill    =  {'技能':技能}
d_tskill    =  {'能做':技能}
d_fskill    =  {'会做':技能}
d_dskill    =  {'懂做':技能}

s_skill    =   {'技术':skill_flag}
s_sskill    =  {'技能':skill_flag}
s_tskill    =  {'能做':skill_flag}
s_fskill    =  {'会做':skill_flag}
s_dskill    =  {'懂做':skill_flag}

#-------------------------------------------------------------------------------------------------
s_what      =  {'什么':what_flag}

s_result    =  {'结果':result_flag}
s_sresult   =  {'后果':result_flag}
s_tresult   =  {'结果':result_flag}

s_hd        =  {'获得':get_flag}
s_sh        =  {'收获':get_flag}
s_dd        =  {'得到':get_flag}
s_hq        =  {'获取':get_flag}
s_yy        =  {'拥有':get_flag}
s_qd        =  {'取得':get_flag}

s_need     =  {'需要':need_flag}
s_sneed    =  {'必需':need_flag}

s_past     = {'前天':past_flag}
s_past     = {'大前天':past_flag}
s_past     = {'前几天':past_flag}
s_past     = {'前段时间':past_flag}
s_past     = {'月前':past_flag}
s_past     = {'个月前':past_flag}
s_past     = {'前几个月':past_flag}

s_past     = {'天前':past_flag}
s_past   =   {'小时前':future_flag}
s_past   =   {'分钟前':future_flag}
s_past   =   {'分秒前':future_flag}

s_past     = {'年前':past_flag}
s_past     = {'前阵':past_flag}
s_past     = {'刚才':past_flag}
s_sast     = {'刚刚':past_flag}
s_tast     = {'已经':past_flag}
s_fpast    = {'成为过去':past_flag}
#----------------------------------------------------------------------------------------------
s_future   = {'明天':future_flag}
s_future   = {'后天':future_flag}
s_future   = {'大后天':future_flag}
s_future   = {'几天后':future_flag}
s_future   = {'过几天':future_flag}
s_future   = {'年后':future_flag}
s_future   = {'天后':future_flag}
s_future   = {'小时后':future_flag}
s_future   = {'分钟后':future_flag}
s_future   = {'分秒后':future_flag}
s_rfuture  = {'准备':future_flag}
s_future   = {'快了':future_flag}
s_future   = {'快到了':future_flag}
s_future   = {'等':future_flag}
s_future   = {'等等':future_flag}
s_mfuture   = {'马上':future_flag}
s_future   = {'尽快':future_flag}
s_future   = {'立即':future_flag}
s_future   = {'等一下':future_flag}
s_future   = {'再等等':future_flag}
s_future   = {'很快了':future_flag}
#------------------------------------------------------------------------------------------------
#s_tnow     = {'今天':now_flag}

s_gtm       = {'早晨':gtime_tm_flag}
s_gtf       = {'上午':gtime_tf_flag}
s_gta       = {'下午':gtime_ta_flag}
s_gtn       = {'晚上':gtime_tn_flag}
s_gtsn      = {'夜晚':gtime_tn_flag}

s_gth       = {'几点':gtime_th_flag}
s_gtm       = {'几分':gtime_tm_flag}
s_gtd       = {'几号':gtime_td_flag}
s_gty       = {'几月':gtime_ty_flag}
s_gtw       = {'周几':gtime_tw_flag}
s_gtx       = {'星期几':gtime_tx_flag}
s_gty       = {'哪年':gtime_ty_flag}

d_ptime      = {'时候':时候}
d_sptime     = {'时':时候}

s_ptime      = {'时候':ptime_flag}
s_sptime     = {'时':ptime_flag}

s_gwt       = {'何时':gtime_wt_flag}
s_gzt       = {'几时':gtime_zt_flag}
s_gst       = {'什么时候':gtime_st_flag}
#/////////////////////////////////////////////////////////////////////////////////////////////////
s_zloc      = {'这':s_zw_flag}#重复含义词

d_floc      = {'哪里':哪里}
d_loccs     = {'在哪里':哪里}
d_tloc      = {'在哪':哪里}
d_fsloc     = {'哪儿':哪里}
d_cln       = {'从哪里':哪里}

s_nloc      = {'那':s_nw_flag}#

s_loccs     = {'在哪里':s_sw_flag}#
s_tloc      = {'在哪':s_znw_flag}

s_floc      = {'哪里':s_nlw_flag}
s_fsloc     = {'哪儿':s_new_flag}
s_cln       = {'从哪里':s_new_flag}

s_hloc      = {'这里':s_zlw_flag}
s_shloc     = {'这边':s_zbw_flag}
s_nhloc     = {'那里':s_lnw_flag}
s_nbloc     = {'那边':s_nbw_flag}
s_zeoc      = {'这儿':s_zew_flag}
s_nlloc     = {'那儿':s_nws_flag}
s_glloc     = {'过来':s_gls_flag}
s_gqloc     = {'过去':s_gqs_flag}
s_dfloc     = {'地方':s_znw_flag}


#s_znltloc   = {'在哪里':s_znlw_flag}
#s_jloc      = {'家':s_jw_flag}#
#s_jlloc     = {'家里':s_jlw_flag}
#s_sfloc     = {'书房':s_sfw_flag}
#s_fjloc     = {'房间':s_fjw_flag}
#s_gsloc     = {'公司':s_gsw_flag}
#s_scloc     = {'商场':s_scw_flag}
#s_gyloc     = {'公园':s_gyw_flag}
#s_yyloc     = {'影院':s_yyw_flag}
#s_jdloc     = {'酒店':s_jdw_flag}
#s_fdloc     = {'饭店':s_fdw_flag}
#s_wuyloc    = {'动物园':s_dwyw_flag}

s_exam     = {'考得':exam_flag}
s_sexam    = {'考试':exam_flag}
s_texam    = {'考核':exam_flag}

d_aok       = {'很好':好}
d_bok       = {'良好':好}
d_cok       = {'优良':好}
d_dok       = {'优秀':好}
d_eok       = {'不错':好}
d_fok       = {'八错':好}
d_gok       = {'好':好}
d_hok       = {'非常好':好}

s_aok       = {'很好':ok_flag}
s_bok       = {'良好':ok_flag}
s_cok       = {'优良':ok_flag}
s_dok       = {'优秀':ok_flag}
s_eok       = {'不错':ok_flag}
s_fok       = {'八错':ok_flag}
s_gok       = {'好':ok_flag}
s_hok       = {'非常好':ok_flag}


s_bad      = {'不好':bad_flag}
s_sbad     = {'糟糕':bad_flag}
s_tad      = {'差劲':bad_flag}
s_fbad     = {'差':bad_flag}
s_buy      = {'买':buy_flag}

s_much      = {'多':much_flag}
s_smuch     = {'很多':much_flag}
s_tmuch     = {'非常多':much_flag}
s_fmuch     = {'更多':much_flag}

s_few       = {'少':few_flag}
s_sfew      = {'很少':few_flag}
s_tfew      = {'非常少':few_flag}
s_ffew      = {'更少':few_flag}

s_tk        = {'太快':fast_flag}
s_hk        = {'很快':fast_flag}
s_gk        = {'更快':fast_flag}
s_fck       = {'非常快':fast_flag}
s_k         = {'快':fast_flag}

s_tur       = {'翻':s_tur}
s_ttur      = {'侧翻':s_tur}
s_dtur      = {'翻倒':s_tur}
s_ftur      = {'翻开':s_tur}

s_open      = {'开':open_flag}
s_sopen     = {'打开':open_flag}

s_which     = {'哪个':s_which}
s_swhich    = {'哪一个':s_which}

s_chi       =  {'吃':chi_flag} 
s_ci        =  {'次':ci_flag}
s_dun       =  {'顿':ci_flag}
s_ds        =  {'几':ds_flag}
s_day       =  {'天':day_flag}
s_mt        =  {'每天':day_flag}
s_yt        =  {'一天':day_flag}

s_sleep     =  {'睡眠':sleep_flag}
s_ssleep    =  {'睡觉':sleep_flag}
s_tsleep    =  {'睡着':sleep_flag}
s_fsleep    =  {'睡':sleep_flag}

s_body      =  {'身体':body_flag }
s_sbody     =  {'躯体':body_flag }
s_tbody     =  {'身子':body_flag }
s_fbody     =  {'身':body_flag }

s_health    =  {'健康':health_flag}
s_shealth   =  {'安康':health_flag}
s_thealth   =  {'平安':health_flag}
s_fhealth   =  {'没事':health_flag}
s_bi        = {'比':bi_flag}
s_big       = {'大':big_flag}
s_small     = {'小':small_flag}

s_rh        =  {'如何':如何}
s_srh       =  {'怎样':如何}
s_trh       =  {'怎么样':如何}
s_frh       =  {'怎么做':如何}

d_if        =  {'如果':如果}
s_if        =  {'如果':if_flag}

d_jiu       =  {'就':就}
d_sjiu      =  {'就要':就}
#d_sjiu      =  {'就能':就}

s_jiu       =  {'就':jiu_flag}
s_sjiu      =  {'就要':jiu_flag}


d_should    =  {'应该':应该}
d_sshould   =  {'应当':应该}

s_should    =  {'应该':should_flag}
s_sshould   =  {'应当':should_flag}
s_lai       =  {'来':lai_flag}
s_ting      =  {'听':ting_flag}
s_tting     =  {'听听':ting_flag}

#d_some      =  {'些':些}
s_some      =  {'些':some_flag}

d_depend    =  {'依靠':依靠}
d_sdepend   =  {'依赖':依靠}

s_depend    =  {'依靠':depend_flag}
s_sdepend   =  {'依赖':depend_flag}

d_lose      =  {'失去':失去}
d_slose     =  {'丢失':失去}
d_tlose     =  {'弄丢':失去}
d_flose     =  {'遗失':失去}

s_lose      =  {'失去':lose_flag}
s_tlose     =  {'丢失':lose_flag}
s_slose     =  {'弄丢':lose_flag}
s_flose     =  {'遗失':lose_flag}

d_power     =  {'电源':电源}
d_spower    =  {'电力':电源}

s_power     =  {'电源':power_flag}
s_spower    =  {'电力':power_flag}

d_memory    =  {'内存':记忆}
d_smemory   =  {'记忆':记忆}
d_smemory   =  {'回忆':记忆}

s_memory    =  {'内存':memory_flag}
s_smemory   =  {'记忆':memory_flag}
s_smemory   =  {'回忆':memory_flag}

d_disk      =  {'磁盘':磁盘}
d_sdisk     =  {'硬盘':磁盘}

s_disk      =  {'磁盘':disk_flag}
s_sdisk     =  {'硬盘':disk_flag}

d_subsist   =  {'生存':生存}
d_ssubsist  =  {'存活':生存}

s_subsist   =  {'生存':subsist_flag}
s_ssubsist  =  {'存活':subsist_flag}

d_not       =  {'不能':不能}
s_not       =  {'不能':not_flag}

d_cant      =  {'无法':无法}
s_cant     =  {'无法':cant_flag}

d_ow        =  {'否则':否则}
s_ow        =  {'否则':ow_flag}

d_separ     =  {'离开':离开}
s_separ     =  {'离开':separ_flag}


#/////////////////////////////////////////////////////////////////////////////////////////////////

d_class_list = [d_money,d_water,d_jlloc,d_jloc,d_car,d_qcar,d_ssp,d_tsp,d_sp
                ,d_zfire,d_zfire,d_sfire,d_wfire,d_fire,d_ap,d_ship,d_lship
                ,d_rl,d_r,d_fan,d_body,d_sbody,d_tbody,d_fbody,d_sun,d_air
                ,d_sman,d_tman,d_fman,d_xman,d_wm,d_swm,d_twm,d_fwm,d_xwm
                ,d_sun,d_moon,d_product,d_pc,d_spc,d_food,d_sfood
                ,d_disk,d_sdisk,d_power,d_spower,d_memory,d_smemory,d_smemory] #注意 

#/////////////////////////////////////////////////////////////////////////////////////////////////
d_okw_class_list =  [d_why,d_whyh,d_whys,d_how,d_much,d_fmuch,d_smuch,d_much,d_buy,d_ftur
                    ,d_fck,d_tk,d_hk,d_gk,d_k,d_tur,d_stur,d_ttur,d_ftur
                    ,d_which,d_swhich,d_ffew,d_chi,d_ci,d_dun,d_ds,d_day,d_mt,d_yt
                    ,d_need,d_sneed,d_cn,d_enough,d_senough,d_keep,d_sleep,d_if
                    ,d_ssleep,d_tsleep,d_fsleep,d_health,d_shealth,d_not,d_ow,d_cant
                    ,d_thealth,d_fhealth,d_bi,d_big,d_rh,d_srh,d_trh,d_frh
                    ,d_hd,d_sh,d_dd,d_hq,d_yy,d_qd,d_tenough,d_none,d_have
                    ,d_result,d_sresult,d_tresult,d_what,d_call,d_scall,d_and
                    ,d_tcall,d_fcall,d_ycall,d_xcall,d_person,d_persons,d_sperson
                    ,d_man,d_or,d_sor,d_tor,d_is,d_ge,d_small,d_create,d_screate,d_tcreate
                    ,d_fcreate,d_code,d_scode,d_exit,d_mission,d_hs,d_should,d_sshould 
                    ,d_smission,d_tmission,d_fmission,d_skeep,d_hight,d_shight,d_separ
                    ,d_differen,d_sdifferen,d_tdifferen,d_now,d_snow,d_sexit
                    ,d_use,d_suse,d_oc,d_soc,d_toc,d_gt,d_jl,d_txt,d_get,d_sget,d_tget
                    ,d_who,d_loccs,d_loccs,d_floc,d_tloc,d_fsloc,d_story,d_humor,d_shumor
                    ,d_skill,d_sskill,d_tskill,d_fskill,d_dskill,d_can,d_mood,d_smood
                    ,d_tcan,d_meet,d_ahappy,d_bhappy,d_chappy,d_dhappy,d_ehappy,d_fhappy,d_ghappy
                    ,d_hhappy,d_ihappy,d_aok,d_bok,d_cok,d_dok,d_eok,d_fok,d_gok,d_hok
                    ,d_open,d_ptime,d_sptime,d_jiu,d_sjiu,d_asad,d_bsad,d_csad,d_dsad
                    ,d_esad,d_fsad,d_gsad,d_hsad,d_isad,d_talk,d_stalk,d_ttalk,d_ftalk
                    ,d_lose,d_slose,d_tlose,d_flose,d_subsist,d_ssubsist]




d_state_list = [s_whyh,s_whys,s_why,s_polite,s_what,s_how
                ,s_le,s_very,s_svery,s_help,s_shelp,s_thelp,s_fhelp
                ,s_get,s_to,s_rfuture,s_mfuture,s_floc,s_gqloc,s_exam
                ,s_sexam ,s_texam,s_bad,s_sbad,s_tad,s_fbad,s_play
                ,s_none,s_snone,s_have,s_buy,s_tmuch,s_fmuch,s_ffew ,s_sfew,s_few,s_tfew,s_sfew,s_few
                ,s_fck,s_hk,s_tk,s_gk,s_k,s_ftur,s_dtur,s_ttur,s_tur,s_sopen
                ,s_which,s_swhich,s_ffew,s_chi,s_ci,s_ds,s_dun,s_mt,s_yt,s_need,s_sneed
                ,s_de,s_enough,s_senough,s_keep,s_sleep,s_if,s_ssleep,s_tsleep,s_fsleep
                ,s_health,s_shealth,s_thealth,s_fhealth,s_bi,s_big,s_hs
                ,s_rh,s_srh,s_trh,s_frh,s_hd,s_sh,s_dd,s_hq,s_yy,s_qd,s_tenough
                ,s_result,s_sresult,s_tresult,s_call,s_scall,s_tcall
                ,s_fcall,s_ycall,s_xcall,s_person,s_persons,s_sperson
                ,s_or,d_sor,d_tor,s_is,s_ge,s_small,s_and,s_create,s_screate,s_tcreate
                ,s_fcreate,s_code,s_scode,s_exit,s_humor,s_shumor
                ,s_mission,s_smission,s_tmission,s_fmission,s_skeep,s_hight,s_shight
                ,s_differen,s_sdifferen,s_tdifferen,s_now,s_snow,s_sexit
                ,s_suse,s_use,s_product,s_gei,s_sgei,s_tgei,s_separ
                ,s_oc,s_soc,s_toc,s_gt,s_jl,s_txt,s_cn,s_not,s_ow,s_cant
                ,s_depend,s_sdepend,s_power,s_spower,s_memory,s_smemory
                ,s_smemory,s_disk,s_sdisk,s_subsist,s_ssubsist
                ,s_or,s_sor,s_who,s_should,s_sshould,s_some
                ,s_loccs,s_loccs,s_floc,s_tloc,s_fsloc,s_mood,s_smood
                ,s_skill,s_sskill,s_tskill,s_fskill,s_can,s_tcan,s_meet,s_story
                ,s_ahappy,s_bhappy,s_chappy,s_dhappy,s_ehappy,s_fhappy,s_ghappy
                ,s_hhappy,s_ihappy,s_aok,s_bok,s_cok,s_dok,s_eok,s_fok,s_gok,s_hok
                ,s_open,s_ptime,s_sptime,s_jiu,s_sjiu,s_lai,s_ting,s_tting
                ,s_asad,s_bsad,s_csad,s_dsad,s_esad,s_fsad,s_gsad,s_hsad,s_isad
                ,s_talk,s_stalk,s_ttalk,s_ftalk,d_depend,d_sdepend                
                ,s_lose,s_slose,s_tlose,s_flose] #注意chi_flag



d_state_curent_list = []

#////////////////////////////////////////////////////////////////////////////////////////////
      
current_match_flag_count = 0
current_match_flag_list = []
key_word_loc = 0
list_counte  = 0

person_class_list = [我(),你(),你们()]

#////////////////////////////////////////////////////////////////////////////////////////////
current_key_word_obj = []*20
#以下是初始化全局变量////////////////////////////////////////////////////////////////////////////
second_person_flag    = False
first_person_flag     = False
thrid_person_flag     = False
person_sum_flag       =False
#////////////////////////////////////////////////////////////////////////////////////////////
t_usr_in_word_len = 0
t_key_pw_loc = 0
t_key_pw_len = 0
t_dc_list = 0
#///////////////////////////////////////////////////////////////////////////////////////////

d_ba_person_list = ['你']

d_ba_list_match =  ['我']


d_ab_person_list = ['我']

d_ab_list_match =  ['你']


d_person_list  = ['你','你们']

d_person_match = ['我','我们']

d_sperson_list = ['我','我们']

d_sperson_match = ['你','你们']

d_person_map = {'你':['人类','人','高级生命']}
current_person_flag_count = 0

current_person_flag = [second_person_flag,first_person_flag,thrid_person_flag,person_sum_flag]

#///////////////////////////////////////////////////////////////////////////////////////////////

#/////////////////////////////////////////////////////////////////////////////////////////////////
def cmp_sim_results(char_list_a,char_list_b):
      pass
#//////////////////////////////////////////////////////////////////////////////////////////////////
#------------------------------------------------------------------------------------------------         
      #print('获得答案',g_g_current_key_word_obj)            
#/////////////////////////////////////////////////////////////////////////////////////////////////
def age_count():
      global current_t
      global born_d
      
      y_c = '岁'
      y_y = '年'
      m_c = '月'
      m_v = '零'
      t_age = '1岁了'

      t = time.strftime('%Y-%m',time.localtime())
      t = time.strptime(t,"%Y-%m")
      y,m = t[0:2]      
      #print(y,m,born_d)
#-------------------------------------------------------------------------------------------------
      y = y - born_d[0]#此处计算年份及月份的关系代码需补充
#-------------------------------------------------------------------------------------------------      
      #此处计算月份代码需补充
#-------------------------------------------------------------------------------------------------
      #print(t_age)
      return t_age
#//////////////////////////////////////////////////////////////////////////////////////////////////
def how_old_count():
      global current_t
      global born_d
      
      y_c = '岁'
      y_y = '年'
      m_c = '月'
      m_v = '零'
      t_age = '1岁零1个月了'

      t = time.strftime('%Y-%m',time.localtime())
      t = time.strptime(t,"%Y-%m")
      y,m = t[0:2]      
      #print(y,m,born_d)
#-------------------------------------------------------------------------------------------------
      y = y - born_d[0]#此处计算年份及月份的关系代码需补充
#-------------------------------------------------------------------------------------------------      
      #此处计算月份代码需补充
#-------------------------------------------------------------------------------------------------
      return t_age
#**************************************************************************************************
def 获得_名称():
      
    global tow_to_five_list
    global d_okw_class_list
    global dy_label
    global key_word_label
    global d_okw_class_list
    global tow_to_five_label
    global first_to_five_label
    global first_to_five_list
    global key_word_list_content
    global ot_label
    global o_label_exit_flag
    global k_symbol_flag
    
    global model_label
    global model_kw

    global model_kw_label_flag
    global model_kw_list
    global model_kw_label
    global ignore_kw_label
    global o_kw_label_flag
    global dy_kw_model_dict
    
    global unidentified_word
    global unidentified_flag
    global unidentified_loc
    
    global model_kw

    global key_word_list
    global first_kw_flag
    global info_word_loc_list
    global fill_kw_loc
    global d_class_list
    global ref_sub_flag
    global p_e_flag
    global s_p_exist_flag
    global conversion_person
    global conversion_usr_info
    
    fill_kw_loc_list = []
    fill_min_loc = 0
    fill_max_loc = 0
    
    fill_wd_add_list   = ''
    before_wd_add_list = ''
    after_wd_add_list  = ''
    
    fill_wd_list = []
    before_wd_list = []
    after_wd_list = []
    before_kw_len = 0
    after_kw_len = 0
    kw_list_all_len = len(info_word_loc_list) - 1

    methods = []
    attribute = []
    obj = []
    
    r_list_content = []
    match_key_list = []
    exclusive_kw = ['名字','姓名','称呼']
    
    ref_sub_kw = ''
    dir_list = '大纲'
    t_obj = ''
    t_obj_len = 0
    t_obj_loc = 0
    answer_obj = ''
    answer_obj_len = 0
    answer_obj_loc = 0
    fill_flag = False
    t_obj_list = ''
    r_obj = ''
    c_obj = ''
    t_r_value = []
    default_obj = []
    answer_list = []
    r_value_flag = False
    compound_dict = {}
    
#---------------------------------------------------------------------------------------------------    
    print('☀☀☀☀模型分析 --->>>>>> 获得_名称',model_kw)
    fill_flag = False
    fill_max_loc = max(fill_kw_loc)
    fill_min_loc = min(fill_kw_loc)
#---------------------------------------------------------------------------------------------------
    if fill_min_loc > 0:
          
       while before_kw_len < fill_min_loc:
             
             before_wd_list.append(info_word_loc_list[before_kw_len])
             before_wd_add_list += info_word_loc_list[before_kw_len]
             print('开始查询前移字符并连接',before_wd_list,before_wd_add_list)
             before_kw_len += 1
             
    before_wd_add_list += model_kw[0] #链接模型关键字        
    answer_list.append(before_wd_add_list)
#---------------------------------------------------------------------------------------------------
    #fill_flag = False
    fill_max_loc = max(fill_kw_loc)
    
    if fill_max_loc < kw_list_all_len:
          
       while fill_max_loc < kw_list_all_len:
             fill_max_loc += 1
             after_wd_list.append(info_word_loc_list[fill_max_loc])
             after_wd_add_list += info_word_loc_list[fill_max_loc]
             print('开始查询后移字符并连接',after_wd_list,after_wd_add_list)
             
    #after_wd_add_list = model_kw[0] + after_wd_add_list #链接模型关键字       
#--------------------------------------------------------------------------------------------------
    #for dyc,ddk in enumerate(dy_kw_model_dict):
           #for dyk,dyv in ddk.items():
              #if dyk == '属性':            
                  #dyv.append(after_wd_add_list)
                  
    #print('更新对应子项信息',dy_kw_model_dict)
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
    #确定对象
    if p_e_flag:
       t_obj = conversion_person  
       print('确定对象',t_obj)
       
    elif key_word_list:
         t_obj = key_word_list[0]
         
    elif tow_to_five_list:
         t_obj = tow_to_five_list[0]      

#---------------------------------------------------------------------------------------------------
    
    for dyc,ddk in enumerate(dy_kw_model_dict):
           for dyk,dyv in ddk.items():
               if dyk == '名字' or dyk == '姓名':            
                  dyv.append(after_wd_add_list)
                
    print('✔✔✔✔更新对应子项信息',dy_kw_model_dict)
#合成新子项填充信息---------------------------------------------------------------------------------------------------

    print('☯☯☯☯检测',answer_list)   
    compound_dict = dict.fromkeys(answer_list,after_wd_add_list)#注意
    print('准备填入对象对应子项信息',compound_dict)
#查询对象并填充信息------------------------------------------------------------------------------------------------------    
    

    if tow_to_five_label:
         ref_sub_kw = tow_to_five_label[0]#此处限定其它关键字总数为一个
         print('▓▓▓▓检测',ref_sub_kw)
         ref_sub_flag = True

    elif key_word_label:
       ref_sub_kw = key_word_label[0]#此处限定第一关键字总数为一个
       print('〓〓〓〓检测',ref_sub_kw)
       ref_sub_flag = True     
         
    if ref_sub_flag == False:
       ref_sub_kw = '属性'   
       print('☎☎☎☎没有对应子项填入默认项',ref_sub_flag)
       
    r_value_flag = hasattr(eval(t_obj),ref_sub_kw)
        

#保存子项对应信息--->>>完成-------------------------------------------------------------------------
    if k_symbol_flag:
       if ref_sub_flag:
             
          c_obj = getattr(eval(t_obj)(),ref_sub_kw)(ref_sub_kw)#从对象获取答案
          print('☁☁☁☁输出答案',c_obj)

       else:
            ref_sub_kw = '名字'
            c_obj = getattr(eval(t_obj)(),ref_sub_kw)(ref_sub_kw)#从对象获取答案
            print('☁☁☁☁输出默认子项答案',c_obj)
       
       
    else:
         for ec,ek in enumerate(exclusive_kw):
             getattr(eval(t_obj)(),ek)(compound_dict) 
    
            #tattr(eval(t_obj)(),ref_sub_kw)(compound_dict)
    
#**************************************************************************************************
def 是_或者():
      
    global tow_to_five_list
    global d_okw_class_list
    global dy_label
    global key_word_label
    global d_okw_class_list
    global tow_to_five_label
    global first_to_five_label
    global first_to_five_list
    global key_word_list_content
    global ot_label
    global o_label_exit_flag
    global k_symbol_flag
    
    global model_label
    global model_kw

    global model_kw_label_flag
    global model_kw_list
    global model_kw_label
    global ignore_kw_label
    global o_kw_label_flag
    global dy_kw_model_dict

    global key_word_list
    global first_kw_flag
    global info_word_loc_list
    global fill_kw_loc
    global d_class_list
    global find_answer_flag
    global ref_sub_flag
    global p_e_flag
    global conversion_person
    
    fill_kw_loc_list = []
    fill_min_loc = 0
    fill_max_loc = 0
    
    fill_wd_add_list   = ''
    before_wd_add_list = ''
    after_wd_add_list  = ''
    
    fill_wd_list = []
    before_wd_list = []
    after_wd_list = []
    before_kw_len = 0
    after_kw_len = 0
    kw_list_all_len = len(info_word_loc_list) - 1

    methods = []
    attribute = []
    obj = []
    
    r_list_content = []
    match_key_list = []
    result = []
    
    ref_sub_kw = ''
    dir_list = '大纲'
    t_obj = ''
    t_obj_len = 0
    t_obj_loc = 0
    answer_obj = ''
    answer_obj_len = 0
    answer_obj_loc = 0
    fill_flag = False
    t_obj_list = ''
    r_obj = ''
    c_obj = ''
    t_r_value = []
    default_obj = []
    answer_list = []
    r_value_flag = False
    f_w_flag = False
    compound_dict = {}   
#---------------------------------------------------------------------------------------------------    
    print('☀☀☀☀模型分析 --->>>>>> 是_或者',model_kw)
    fill_flag = False
    fill_max_loc = max(fill_kw_loc)
    fill_min_loc = min(fill_kw_loc)
#---------------------------------------------------------------------------------------------------
    print('复查',model_kw_list,info_word_loc_list)
    print('填充前范围计算',fill_kw_loc,fill_min_loc,fill_max_loc)
#---------------------------------------------------------------------------------------------------
    while fill_min_loc < fill_max_loc - 1:
          fill_min_loc += 1
          fill_wd_list.append(info_word_loc_list[fill_min_loc])
          fill_wd_add_list = fill_wd_add_list + info_word_loc_list[fill_min_loc]
          answer_list.append(fill_wd_add_list)
          print('开始填充并连接',fill_wd_list,fill_wd_add_list)
#---------------------------------------------------------------------------------------------------
    fill_min_loc = min(fill_kw_loc)
    #fill_max_loc = max(fill_kw_loc) - 1

    if fill_min_loc > 0:
          
       while before_kw_len < fill_min_loc:
             
             before_wd_list.append(info_word_loc_list[before_kw_len])
             before_wd_add_list += info_word_loc_list[before_kw_len]
             print('开始查询前移字符并连接',before_wd_list,before_wd_add_list)
             before_kw_len += 1
#---------------------------------------------------------------------------------------------------
    #t_obj = before_wd_add_list #确定对象，必要时去查询一下对象类列表验证对象是否存在,现在默认为存在
    #确定对象
    if p_e_flag:
       t_obj = conversion_person  
       print('确定对象',t_obj)
       
    elif key_word_list:
         t_obj = key_word_list[0]
         
    elif tow_to_five_list:
         t_obj = tow_to_five_list[0]

    print('✔✔✔✔确定对象',t_obj)

#---------------------------------------------------------------------------------------------------
    fill_flag = False
    fill_max_loc = max(fill_kw_loc)
    
    if fill_max_loc < kw_list_all_len:
          
       while fill_max_loc < kw_list_all_len:
             fill_max_loc += 1
             after_wd_list.append(info_word_loc_list[fill_max_loc])
             after_wd_add_list += info_word_loc_list[fill_max_loc]
             answer_list.append(after_wd_add_list)
             print('开始查询后移字符并连接',after_wd_list,after_wd_add_list)

    print('▶▶▶▶候选选择列表',answer_list)

#获取答案--------------------------------------------------------------------------------------------------
    if key_word_label:
       ref_sub_kw = key_word_label[0]
    elif tow_to_five_label:
         ref_sub_kw = tow_to_five_label[0]

    for alc,alk in enumerate(answer_list):
          
        result = getattr(eval(t_obj)(),ref_sub_kw)(alk)
        
        if find_answer_flag:
           print('♏♏♏♏对应子项',ref_sub_kw)   
           print('☁☁☁☁输出答案',result)
           break

        else:
           print('找不到答案',find_answer_flag)
#**************************************************************************************************
def 行为_对象():
      
    global tow_to_five_list
    global d_okw_class_list
    global dy_label
    global key_word_label
    global d_okw_class_list
    global tow_to_five_label
    global first_to_five_label
    global first_to_five_list
    global key_word_list_content
    global ot_label
    global o_label_exit_flag
    global k_symbol_flag
    
    global model_label
    global model_kw
    global model_exit_flag

    global model_kw_label_flag
    global model_kw_list
    global model_kw_label
    global ignore_kw_label
    global o_kw_label_flag
    global dy_kw_model_dict
    
    global unidentified_word
    global unidentified_flag
    global unidentified_loc

    global smodel_kw_sum
    global smodel_kw_list
    global smodel_kw_label
    
    global model_kw

    global key_word_list
    global first_kw_flag
    global info_word_loc_list
    global fill_kw_loc
    global d_class_list
    global ref_sub_flag
    global p_e_flag
    global s_p_exist_flag
    global conversion_person
    global conversion_usr_info
    global storage_usr_info
    global preset_why
    global compen_label_flag
    global tow_to_five_exit_flag
    global model_exit_flag
    global smodel_exit_flag
    global original_tow_to_five_list
    
    fill_kw_loc_list = []
    fill_min_loc = 0
    fill_max_loc = 0
    
    fill_wd_add_list   = ''
    before_wd_add_list = ''
    after_wd_add_list  = ''
    
    fill_wd_list = []
    before_wd_list = []
    after_wd_list = []
    before_kw_len = 0
    after_kw_len = 0
    kw_list_all_len = len(info_word_loc_list) - 1

    methods = []
    attribute = []
    obj = []
    ref_dir_list = ['技能','能力']
    preset = '哦'

    seer_array = ''
    seer_list = []
    r_list_content = []
    match_key_list = []
    
    ref_sub_kw = ''
    dir_list = '大纲'
    t_obj = ''
    t_obj_len = 0
    t_obj_loc = 0
    answer_obj = ''
    answer_obj_len = 0
    answer_obj_loc = 0
    fill_flag = False
    t_obj_list = ''
    r_obj = ''
    c_obj = '对象'
    t_r_value = []
    default_obj = []
    answer_list = []
    r_value_flag = False
    compound_dict = {}
    
#---------------------------------------------------------------------------------------------------    
    print('☀☀☀☀模型分析 --->>>>>> 行为_对象',model_kw,model_exit_flag)
    fill_flag = False
    fill_max_loc = max(fill_kw_loc)
    fill_min_loc = min(fill_kw_loc)
#以下代码将确定执行行为的对象而不是出现在原始语句中的对象作为执行对象---------------------------------------------------------------------------------------------------
    #if p_e_flag:
       #t_obj = conversion_person  
       #print('✪✪✪✪确定对象',t_obj)
       
    #elif first_kw_flag:
         #t_obj = key_word_list[0]
         #print('❤❤❤❤确定对象',t_obj,key_word_list)
         
    if original_tow_to_five_list:#original_tow_to_five_list
         for ttc,ttk in enumerate(original_tow_to_five_list):
             for dcc,dkk in enumerate(d_okw_class_list):
                 for doc,dok in dkk.items():
                     if doc == ttk:
                        r_value_flag = hasattr(dok(),c_obj)
                        if r_value_flag:
                           t_r_value = getattr(dok(),c_obj)()
                           t_obj = t_r_value[0]
                           print('♔♔♔♔确定对象:',t_obj)
#---------------------------------------------------------------------------------------------------
    if tow_to_five_label and ref_sub_flag == False:

         for tc,tk in enumerate(tow_to_five_label):
             #print('看这里',tk)  
             r_value_flag = hasattr(eval(t_obj),tk)#检测对象是否存在对应子项
             if r_value_flag:
                ref_sub_kw = tk#此处限定其它关键字总数为一个
                ref_dir_list.append(ref_sub_kw)
                ref_sub_flag = True
         print('▓▓▓▓检测',ref_sub_kw)
         

    if smodel_kw_label and ref_sub_flag == False:

         for sc,sk in enumerate(smodel_kw_label):
             #print('看这里',sk)  
             r_value_flag = hasattr(eval(t_obj),sk)#检测对象是否存在对应子项
             if r_value_flag:
                ref_sub_kw = sk#此处限定其它关键字总数为一个
                ref_dir_list.append(ref_sub_kw)
                ref_sub_flag = True 

         print('♦♦♦♦检测',ref_sub_kw)
     

    if key_word_label and ref_sub_flag == False:

       for kc,kk in enumerate(smodel_kw_label):
             #print('看这里',kk)  
             r_value_flag = hasattr(eval(t_obj),kk)#检测对象是否存在对应子项
             if r_value_flag:
                ref_sub_kw = kk#此处限定其它关键字总数为一个
                ref_dir_list.append(ref_sub_kw)
                ref_sub_flag = True    
    
       print('〓〓〓〓检测',ref_sub_kw)
    
         
    if ref_sub_flag == False:
       ref_sub_kw = '行为'   
       print('☎☎☎☎没有对应子项填入默认项',ref_sub_flag,ref_sub_kw)
#---------------------------------------------------------------------------------------------------
    if fill_min_loc > 0:
          
       while before_kw_len < fill_min_loc:
             
             before_wd_list.append(info_word_loc_list[before_kw_len])
             before_wd_add_list += info_word_loc_list[before_kw_len]             
             before_kw_len += 1
             print('开始查询前移字符并连接',before_wd_list,before_wd_add_list)
                          
    before_wd_add_list += model_kw[0] #链接模型关键字        
    answer_list.append(before_wd_add_list)
#---------------------------------------------------------------------------------------------------
    while fill_min_loc < fill_max_loc:
          fill_min_loc += 1
          fill_wd_list.append(info_word_loc_list[fill_min_loc])
          fill_wd_add_list = fill_wd_add_list + info_word_loc_list[fill_min_loc]
          print('开始填充并连接',fill_wd_list,fill_wd_add_list)  
#---------------------------------------------------------------------------------------------------
    #fill_flag = False
    fill_max_loc = max(fill_kw_loc)
    
    if fill_max_loc < kw_list_all_len:
          
       while fill_max_loc < kw_list_all_len:
             fill_max_loc += 1
             after_wd_list.append(info_word_loc_list[fill_max_loc])
             after_wd_add_list += info_word_loc_list[fill_max_loc]
             print('开始查询后移字符并连接',after_wd_list,after_wd_add_list)
             
    #after_wd_add_list = model_kw[0] + after_wd_add_list #链接模型关键字       
#----------------------------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#合成新子项填充信息---------------------------------------------------------------------------------------------------

    #print('☯☯☯☯检测',answer_list)   
    #compound_dict = dict.fromkeys(answer_list,after_wd_add_list)#注意
    #print('准备填入对象对应子项信息',compound_dict,model_exit_flag)
#查询对象并填充信息------------------------------------------------------------------------------------------------------        

    if k_symbol_flag == False:#判断语句性质(学习/询问/倾诉)

       #for rcc ,rkk in enumerate(ref_dir_list):      
           #r_value_flag = hasattr(eval(t_obj),rkk)    
           #if r_value_flag:
       
              #getattr(eval(t_obj)(),rkk)(compound_dict)
              
           #else:
               #print('✘✘✘✘对象没有对应子项:',ref_sub_kw)
    #else: #t_obj ref_sub_kw before_wd_add_list after_wd_add_list back_wd
        #r_obj = acquire_resule(t_obj,ref_sub_kw,before_wd_add_list,after_wd_add_list)
        #if r_obj:
           #print('☁☁☁☁获取答案:',r_obj)
        #else:
           #print('☡☡☡☡获取答案失败:',r_obj)
#--------------------------------------------------------------------------------------------------

    #if k_symbol_flag:
       r_value_flag = hasattr(eval(t_obj),ref_sub_kw)
       if r_value_flag:
          print('✔✔✔✔对象存在对应子项:',ref_sub_kw)
          c_obj = model_kw[0]
          seer_array =  getattr(eval(t_obj)(),ref_sub_kw)(fill_wd_add_list + after_wd_add_list)
          #r_obj = t_obj +  c_obj + preset
          print('☁☁☁☁获取答案:',r_obj)
          print(seer_array)
       else:
          print('✘✘✘✘对象没有对应子项:',ref_sub_kw)   
       
    #else:
        #print('☯☯☯☯检测',answer_list)   
        #compound_dict = dict.fromkeys(answer_list,after_wd_add_list)#注意
        #print('准备填入对象对应子项信息',compound_dict)
#查询对象并填充信息------------------------------------------------------------------------------------------------------        
       
        #for rcc ,rkk in enumerate(ref_dir_list):      
            #r_value_flag = hasattr(eval(t_obj),rkk)

    
            #if r_value_flag:
       
               #getattr(eval(t_obj)(),rkk)(compound_dict)

#**************************************************************************************************
def 能力_范围():
      
      
    global tow_to_five_list
    global d_okw_class_list
    global dy_label
    global key_word_label
    global d_okw_class_list
    global tow_to_five_label
    global first_to_five_label
    global first_to_five_list
    global key_word_list_content
    global ot_label
    global o_label_exit_flag
    global k_symbol_flag
    
    global model_label
    global model_kw

    global model_kw_label_flag
    global model_kw_list
    global model_kw_label
    global ignore_kw_label
    global o_kw_label_flag
    global dy_kw_model_dict
    
    global unidentified_word
    global unidentified_flag
    global unidentified_loc

    global smodel_kw_sum
    global smodel_kw_list
    global smodel_kw_label
    
    global model_kw

    global key_word_list
    global first_kw_flag
    global info_word_loc_list
    global fill_kw_loc
    global d_class_list
    global ref_sub_flag
    global p_e_flag
    global s_p_exist_flag
    global conversion_person
    global conversion_usr_info
    global storage_usr_info
    global preset_why
    global compen_label_flag
    global tow_to_five_exit_flag
    global model_exit_flag
    global smodel_exit_flag
    global original_tow_to_five_list
    
    fill_kw_loc_list = []
    fill_min_loc = 0
    fill_max_loc = 0
    
    fill_wd_add_list   = ''
    before_wd_add_list = ''
    after_wd_add_list  = ''
    
    fill_wd_list = []
    before_wd_list = []
    after_wd_list = []
    before_kw_len = 0
    after_kw_len = 0
    kw_list_all_len = len(info_word_loc_list) - 1

    methods = []
    attribute = []
    obj = []
    ref_dir_list = ['技能','能力']
    deny = '什么都不会哦'
    preset = '和'

    seer_array = ''
    seer_list = []
    r_list_content = []
    match_key_list = []
    
    ref_sub_kw = ''
    dir_list = '大纲'
    t_obj = ''
    t_obj_len = 0
    t_obj_loc = 0
    answer_obj = ''
    answer_obj_len = 0
    answer_obj_loc = 0
    fill_flag = False
    t_obj_list = ''
    r_obj = ''
    c_obj = '对象'
    t_r_value = []
    default_obj = []
    answer_list = []
    r_value_flag = False
    compound_dict = {}
    
#---------------------------------------------------------------------------------------------------    
    print('☀☀☀☀模型分析 --->>>>>> 能力_范围',model_kw)
    fill_flag = False
    fill_max_loc = max(fill_kw_loc)
    fill_min_loc = min(fill_kw_loc)
#---------------------------------------------------------------------------------------------------
    if p_e_flag:
       t_obj = conversion_person  
       print('✪✪✪✪确定对象',t_obj)
       
    elif first_kw_flag:
         t_obj = key_word_list[0]
         print('❤❤❤❤确定对象',t_obj,key_word_list)
         
    elif original_tow_to_five_list:#original_tow_to_five_list
         for ttc,ttk in enumerate(original_tow_to_five_list):
             for dcc,dkk in enumerate(d_okw_class_list):
                 for doc,dok in dkk.items():
                     if doc == ttk:
                        r_value_flag = hasattr(dok(),c_obj)
                        if r_value_flag:
                           t_r_value = getattr(dok(),c_obj)()
                           t_obj = t_r_value[0]
                           print('♔♔♔♔确定对象:',t_obj)
#---------------------------------------------------------------------------------------------------
    if tow_to_five_label and ref_sub_flag == False:

         for tc,tk in enumerate(tow_to_five_label):
             #print('看这里',tk)  
             r_value_flag = hasattr(eval(t_obj),tk)#检测对象是否存在对应子项
             if r_value_flag:
                ref_sub_kw = tk#此处限定其它关键字总数为一个
                ref_dir_list.append(ref_sub_kw)
                ref_sub_flag = True
         print('▓▓▓▓检测',ref_sub_kw)
         

    if smodel_kw_label and ref_sub_flag == False:

         for sc,sk in enumerate(smodel_kw_label):
             print('看这里',sk)  
             r_value_flag = hasattr(eval(t_obj),sk)#检测对象是否存在对应子项
             if r_value_flag:
                ref_sub_kw = sk#此处限定其它关键字总数为一个
                ref_dir_list.append(ref_sub_kw)
                ref_sub_flag = True 

         print('♦♦♦♦检测',ref_sub_kw)
     

    if key_word_label and ref_sub_flag == False:

       for kc,kk in enumerate(smodel_kw_label):
             #print('看这里',kk)  
             r_value_flag = hasattr(eval(t_obj),kk)#检测对象是否存在对应子项
             if r_value_flag:
                ref_sub_kw = kk#此处限定其它关键字总数为一个
                ref_dir_list.append(ref_sub_kw)
                ref_sub_flag = True    
    
       print('〓〓〓〓检测',ref_sub_kw)
    
         
    if ref_sub_flag == False:
       ref_sub_kw = '技能'   
       print('☎☎☎☎没有对应子项填入默认项',ref_sub_flag,ref_dir_list)
#---------------------------------------------------------------------------------------------------
    if fill_min_loc > 0:
          
       while before_kw_len < fill_min_loc:
             
             before_wd_list.append(info_word_loc_list[before_kw_len])
             before_wd_add_list += info_word_loc_list[before_kw_len]             
             before_kw_len += 1
             print('开始查询前移字符并连接',before_wd_list,before_wd_add_list)
                          
    before_wd_add_list += model_kw[0] #链接模型关键字        
    answer_list.append(before_wd_add_list)
#---------------------------------------------------------------------------------------------------
  
#---------------------------------------------------------------------------------------------------
    #fill_flag = False
    fill_max_loc = max(fill_kw_loc)
    
    if fill_max_loc < kw_list_all_len:
          
       while fill_max_loc < kw_list_all_len:
             fill_max_loc += 1
             after_wd_list.append(info_word_loc_list[fill_max_loc])
             after_wd_add_list += info_word_loc_list[fill_max_loc]
             print('开始查询后移字符并连接',after_wd_list,after_wd_add_list)
             
    #after_wd_add_list = model_kw[0] + after_wd_add_list #链接模型关键字       
#----------------------------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#合成新子项填充信息---------------------------------------------------------------------------------------------------

    #print('☯☯☯☯检测',answer_list)   
    compound_dict = dict.fromkeys(answer_list,after_wd_add_list)#注意
    print('准备填入对象对应子项信息',compound_dict)
#查询对象并填充信息------------------------------------------------------------------------------------------------------        
#--------------------------------------------------------------------------------------------------

    if k_symbol_flag:
       r_value_flag = hasattr(eval(t_obj),ref_sub_kw)
       if r_value_flag:
          print('✔✔✔✔对象存在对应子项:',ref_sub_kw)
          c_obj = model_kw[0]
          seer_array =  getattr(eval(t_obj)(),ref_sub_kw)(after_wd_add_list)
          print('ிிிி获取答案:',seer_array)
          if seer_array:# != False:
             r_value_flag = isinstance(seer_array, list)
             if r_value_flag:
                for  sc,sk in enumerate(seer_array):
                     r_obj += sk 
                     print('☁☁☁☁获取答案:',r_obj)

          else:
              seer_array = t_obj + deny# + c_obj + preset
             
              print('♛♛♛♛获取答案:',seer_array)
                
             
       else:
          print('✘✘✘✘对象没有对应子项:',ref_sub_kw)   
       
    else:
        print('☯☯☯☯检测',answer_list)   
        compound_dict = dict.fromkeys(answer_list,after_wd_add_list)#注意
        print('准备填入对象对应子项信息',compound_dict)
#查询对象并填充信息------------------------------------------------------------------------------------------------------        
       
        for rcc ,rkk in enumerate(ref_dir_list):      
            r_value_flag = hasattr(eval(t_obj),rkk)

    
            if r_value_flag:
       
               getattr(eval(t_obj)(),rkk)(compound_dict)

#**************************************************************************************************
def 行为_描述():
      
    global tow_to_five_list
    global d_okw_class_list
    global dy_label
    global key_word_label
    global d_okw_class_list
    global tow_to_five_label
    global first_to_five_label
    global first_to_five_list
    global key_word_list_content
    global ot_label
    global o_label_exit_flag
    global k_symbol_flag
    
    global model_label
    global model_kw
    global model_exit_flag

    global model_kw_label_flag
    global model_kw_list
    global model_kw_label
    global ignore_kw_label
    global o_kw_label_flag
    global dy_kw_model_dict
    
    global unidentified_word
    global unidentified_flag
    global unidentified_loc

    global smodel_kw_sum
    global smodel_kw_list
    global smodel_kw_label
    
    global model_kw

    global key_word_list
    global first_kw_flag
    global info_word_loc_list
    global fill_kw_loc
    global d_class_list
    global ref_sub_flag
    global p_e_flag
    global s_p_exist_flag
    global conversion_person
    global conversion_usr_info
    global storage_usr_info
    global preset_why
    global compen_label_flag
    global tow_to_five_exit_flag
    global model_exit_flag
    global smodel_exit_flag
    global original_tow_to_five_list
    
    fill_kw_loc_list = []
    fill_min_loc = 0
    fill_max_loc = 0
    
    fill_wd_add_list   = ''
    before_wd_add_list = ''
    after_wd_add_list  = ''
    
    fill_wd_list = []
    before_wd_list = []
    after_wd_list = []
    before_kw_len = 0
    after_kw_len = 0
    kw_list_all_len = len(info_word_loc_list) - 1

    methods = []
    attribute = []
    obj = []
    ref_dir_list = ['技能','能力']
    preset = '哦'

    seer_array = ''
    seer_list = []
    r_list_content = []
    match_key_list = []
    
    ref_sub_kw = ''
    dir_list = '大纲'
    t_obj = ''
    t_obj_len = 0
    t_obj_loc = 0
    answer_obj = ''
    answer_obj_len = 0
    answer_obj_loc = 0
    fill_flag = False
    t_obj_list = ''
    r_obj = ''
    c_obj = '对象'
    t_r_value = []
    default_obj = []
    answer_list = []
    r_value_flag = False
    compound_dict = {}
    
#---------------------------------------------------------------------------------------------------    
    print('☀☀☀☀模型分析 --->>>>>> 行为_描述',model_kw,model_exit_flag)
    fill_flag = False
    fill_max_loc = max(fill_kw_loc)
    fill_min_loc = min(fill_kw_loc)
#---------------------------------------------------------------------------------------------------
    if p_e_flag:
       t_obj = conversion_person  
       print('✪✪✪✪确定对象',t_obj)
       
    elif first_kw_flag:
         t_obj = key_word_list[0]
         print('❤❤❤❤确定对象',t_obj,key_word_list)
         
    elif original_tow_to_five_list:#original_tow_to_five_list
         for ttc,ttk in enumerate(original_tow_to_five_list):
             for dcc,dkk in enumerate(d_okw_class_list):
                 for doc,dok in dkk.items():
                     if doc == ttk:
                        r_value_flag = hasattr(dok(),c_obj)
                        if r_value_flag:
                           t_r_value = getattr(dok(),c_obj)()
                           t_obj = t_r_value[0]
                           print('♔♔♔♔确定对象:',t_obj)
#---------------------------------------------------------------------------------------------------
    if tow_to_five_label and ref_sub_flag == False:

         for tc,tk in enumerate(tow_to_five_label):
             #print('看这里',tk)  
             r_value_flag = hasattr(eval(t_obj),tk)#检测对象是否存在对应子项
             if r_value_flag:
                ref_sub_kw = tk#此处限定其它关键字总数为一个
                ref_dir_list.append(ref_sub_kw)
                ref_sub_flag = True
         print('▓▓▓▓检测',ref_sub_kw)
         

    if smodel_kw_label and ref_sub_flag == False:

         for sc,sk in enumerate(smodel_kw_label):
             #print('看这里',sk)  
             r_value_flag = hasattr(eval(t_obj),sk)#检测对象是否存在对应子项
             if r_value_flag:
                ref_sub_kw = sk#此处限定其它关键字总数为一个
                ref_dir_list.append(ref_sub_kw)
                ref_sub_flag = True 

         print('♦♦♦♦检测',ref_sub_kw)
     

    if key_word_label and ref_sub_flag == False:

       for kc,kk in enumerate(smodel_kw_label):
             #print('看这里',kk)  
             r_value_flag = hasattr(eval(t_obj),kk)#检测对象是否存在对应子项
             if r_value_flag:
                ref_sub_kw = kk#此处限定其它关键字总数为一个
                ref_dir_list.append(ref_sub_kw)
                ref_sub_flag = True    
    
       print('〓〓〓〓检测',ref_sub_kw)
    
         
    if ref_sub_flag == False:
       ref_sub_kw = '行为'   
       print('☎☎☎☎没有对应子项填入默认项',ref_sub_flag,ref_sub_kw)
#---------------------------------------------------------------------------------------------------
    if fill_min_loc > 0:
          
       while before_kw_len < fill_min_loc:
             
             before_wd_list.append(info_word_loc_list[before_kw_len])
             before_wd_add_list += info_word_loc_list[before_kw_len]             
             before_kw_len += 1
             print('开始查询前移字符并连接',before_wd_list,before_wd_add_list)
                          
    before_wd_add_list += model_kw[0] #链接模型关键字        
    answer_list.append(before_wd_add_list)
#---------------------------------------------------------------------------------------------------
  
#---------------------------------------------------------------------------------------------------
    #fill_flag = False
    fill_max_loc = max(fill_kw_loc)
    
    if fill_max_loc < kw_list_all_len:
          
       while fill_max_loc < kw_list_all_len:
             fill_max_loc += 1
             after_wd_list.append(info_word_loc_list[fill_max_loc])
             after_wd_add_list += info_word_loc_list[fill_max_loc]
             print('开始查询后移字符并连接',after_wd_list,after_wd_add_list)
             
    #after_wd_add_list = model_kw[0] + after_wd_add_list #链接模型关键字       
#----------------------------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#合成新子项填充信息---------------------------------------------------------------------------------------------------

    #print('☯☯☯☯检测',answer_list)   
    #compound_dict = dict.fromkeys(answer_list,after_wd_add_list)#注意
    #print('准备填入对象对应子项信息',compound_dict,model_exit_flag)
#查询对象并填充信息------------------------------------------------------------------------------------------------------        

    if k_symbol_flag == False:#判断语句性质(学习/询问/倾诉)

       #for rcc ,rkk in enumerate(ref_dir_list):      
           #r_value_flag = hasattr(eval(t_obj),rkk)    
           #if r_value_flag:
       
              #getattr(eval(t_obj)(),rkk)(compound_dict)
              
           #else:
               #print('✘✘✘✘对象没有对应子项:',ref_sub_kw)
    #else: #t_obj ref_sub_kw before_wd_add_list after_wd_add_list back_wd
        #r_obj = acquire_resule(t_obj,ref_sub_kw,before_wd_add_list,after_wd_add_list)
        #if r_obj:
           #print('☁☁☁☁获取答案:',r_obj)
        #else:
           #print('☡☡☡☡获取答案失败:',r_obj)
#--------------------------------------------------------------------------------------------------

    #if k_symbol_flag:
       r_value_flag = hasattr(eval(t_obj),ref_sub_kw)
       if r_value_flag:
          print('✔✔✔✔对象存在对应子项:',ref_sub_kw)
          c_obj = model_kw[0]
          seer_array =  getattr(eval(t_obj)(),ref_sub_kw)(after_wd_add_list)
          r_obj = t_obj +  c_obj + preset
          print('☁☁☁☁获取答案:',r_obj)
          print(seer_array)
       else:
          print('✘✘✘✘对象没有对应子项:',ref_sub_kw)   
       
    #else:
        #print('☯☯☯☯检测',answer_list)   
        #compound_dict = dict.fromkeys(answer_list,after_wd_add_list)#注意
        #print('准备填入对象对应子项信息',compound_dict)
#查询对象并填充信息------------------------------------------------------------------------------------------------------        
       
        #for rcc ,rkk in enumerate(ref_dir_list):      
            #r_value_flag = hasattr(eval(t_obj),rkk)

    
            #if r_value_flag:
       
               #getattr(eval(t_obj)(),rkk)(compound_dict)  
#**************************************************************************************************
def 意向_能力():
      
    global tow_to_five_list
    global d_okw_class_list
    global dy_label
    global key_word_label
    global d_okw_class_list
    global tow_to_five_label
    global first_to_five_label
    global first_to_five_list
    global key_word_list_content
    global ot_label
    global o_label_exit_flag
    global k_symbol_flag
    
    global model_label
    global model_kw

    global model_kw_label_flag
    global model_kw_list
    global model_kw_label
    global ignore_kw_label
    global o_kw_label_flag
    global dy_kw_model_dict
    
    global unidentified_word
    global unidentified_flag
    global unidentified_loc

    global smodel_kw_sum
    global smodel_kw_list
    global smodel_kw_label
    
    global model_kw

    global key_word_list
    global first_kw_flag
    global info_word_loc_list
    global fill_kw_loc
    global d_class_list
    global ref_sub_flag
    global p_e_flag
    global s_p_exist_flag
    global conversion_person
    global conversion_usr_info
    global storage_usr_info
    global preset_why
    global compen_label_flag
    global tow_to_five_exit_flag
    global model_exit_flag
    global smodel_exit_flag
    global original_tow_to_five_list
    
    fill_kw_loc_list = []
    fill_min_loc = 0
    fill_max_loc = 0
    
    fill_wd_add_list   = ''
    before_wd_add_list = ''
    after_wd_add_list  = ''
    
    fill_wd_list = []
    before_wd_list = []
    after_wd_list = []
    before_kw_len = 0
    after_kw_len = 0
    kw_list_all_len = len(info_word_loc_list) - 1

    methods = []
    attribute = []
    obj = []
    ref_dir_list = ['技能','能力']
    deny = '不'
    preset = '哦'

    seer_array = ''
    seer_list = []
    r_list_content = []
    match_key_list = []
    
    ref_sub_kw = ''
    dir_list = '大纲'
    t_obj = ''
    t_obj_len = 0
    t_obj_loc = 0
    answer_obj = ''
    answer_obj_len = 0
    answer_obj_loc = 0
    fill_flag = False
    t_obj_list = ''
    r_obj = ''
    c_obj = '对象'
    t_r_value = []
    default_obj = []
    answer_list = []
    r_value_flag = False
    compound_dict = {}
    
#---------------------------------------------------------------------------------------------------    
    print('☀☀☀☀模型分析 --->>>>>> 意向_能力',model_kw)
    fill_flag = False
    fill_max_loc = max(fill_kw_loc)
    fill_min_loc = min(fill_kw_loc)
#---------------------------------------------------------------------------------------------------
    if p_e_flag:
       t_obj = conversion_person  
       print('✪✪✪✪确定对象',t_obj)
       
    elif first_kw_flag:
         t_obj = key_word_list[0]
         print('❤❤❤❤确定对象',t_obj,key_word_list)
         
    elif original_tow_to_five_list:#original_tow_to_five_list
         for ttc,ttk in enumerate(original_tow_to_five_list):
             for dcc,dkk in enumerate(d_okw_class_list):
                 for doc,dok in dkk.items():
                     if doc == ttk:
                        r_value_flag = hasattr(dok(),c_obj)
                        if r_value_flag:
                           t_r_value = getattr(dok(),c_obj)()
                           t_obj = t_r_value[0]
                           print('♔♔♔♔确定对象:',t_obj)
#---------------------------------------------------------------------------------------------------
    if tow_to_five_label and ref_sub_flag == False:

         for tc,tk in enumerate(tow_to_five_label):
             #print('看这里',tk)  
             r_value_flag = hasattr(eval(t_obj),tk)#检测对象是否存在对应子项
             if r_value_flag:
                ref_sub_kw = tk#此处限定其它关键字总数为一个
                ref_dir_list.append(ref_sub_kw)
                ref_sub_flag = True
         print('▓▓▓▓检测',ref_sub_kw)
         

    if smodel_kw_label and ref_sub_flag == False:

         for sc,sk in enumerate(smodel_kw_label):
             print('看这里',sk)  
             r_value_flag = hasattr(eval(t_obj),sk)#检测对象是否存在对应子项
             if r_value_flag:
                ref_sub_kw = sk#此处限定其它关键字总数为一个
                ref_dir_list.append(ref_sub_kw)
                ref_sub_flag = True 

         print('♦♦♦♦检测',ref_sub_kw)
     

    if key_word_label and ref_sub_flag == False:

       for kc,kk in enumerate(smodel_kw_label):
             #print('看这里',kk)  
             r_value_flag = hasattr(eval(t_obj),kk)#检测对象是否存在对应子项
             if r_value_flag:
                ref_sub_kw = kk#此处限定其它关键字总数为一个
                ref_dir_list.append(ref_sub_kw)
                ref_sub_flag = True    
    
       print('〓〓〓〓检测',ref_sub_kw)
    
         
    if ref_sub_flag == False:
       ref_sub_kw = '技能'   
       print('☎☎☎☎没有对应子项填入默认项',ref_sub_flag,ref_dir_list)
#---------------------------------------------------------------------------------------------------
    if fill_min_loc > 0:
          
       while before_kw_len < fill_min_loc:
             
             before_wd_list.append(info_word_loc_list[before_kw_len])
             before_wd_add_list += info_word_loc_list[before_kw_len]             
             before_kw_len += 1
             print('开始查询前移字符并连接',before_wd_list,before_wd_add_list)
                          
    before_wd_add_list += model_kw[0] #链接模型关键字        
    answer_list.append(before_wd_add_list)
#---------------------------------------------------------------------------------------------------
  
#---------------------------------------------------------------------------------------------------
    #fill_flag = False
    fill_max_loc = max(fill_kw_loc)
    
    if fill_max_loc < kw_list_all_len:
          
       while fill_max_loc < kw_list_all_len:
             fill_max_loc += 1
             after_wd_list.append(info_word_loc_list[fill_max_loc])
             after_wd_add_list += info_word_loc_list[fill_max_loc]
             print('开始查询后移字符并连接',after_wd_list,after_wd_add_list)
             
    #after_wd_add_list = model_kw[0] + after_wd_add_list #链接模型关键字       
#----------------------------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#合成新子项填充信息---------------------------------------------------------------------------------------------------

    #print('☯☯☯☯检测',answer_list)   
    compound_dict = dict.fromkeys(answer_list,after_wd_add_list)#注意
    print('准备填入对象对应子项信息',compound_dict)
#查询对象并填充信息------------------------------------------------------------------------------------------------------        
#--------------------------------------------------------------------------------------------------

    if k_symbol_flag:
       r_value_flag = hasattr(eval(t_obj),ref_sub_kw)
       if r_value_flag:
          print('✔✔✔✔对象存在对应子项:',ref_sub_kw)
          c_obj = model_kw[0]
          seer_array =  getattr(eval(t_obj)(),ref_sub_kw)(after_wd_add_list)
          #print('ிிிி获取答案:',seer_array)
          if seer_array:# != False:
             #print('☄☄☄☄查看返回值:',type(seer_array))   
             seer_array = t_obj +  c_obj + preset
             
             print('☁☁☁☁获取答案:',seer_array)
             r_obj = smodel_kw_label[0]#获得肯定回复后提前预设信息输出(取自二级关键字标签)
             seer_array =  getattr(eval(t_obj)(),r_obj)(after_wd_add_list)
             print('♚♚♚♚获取答案:',seer_array)
          else:
              seer_array = t_obj + deny + c_obj + preset
             
              print('☁☁☁☁获取答案:',seer_array)
                
             
       else:
          print('✘✘✘✘对象没有对应子项:',ref_sub_kw)   
       
    else:
        print('☯☯☯☯检测',answer_list)   
        compound_dict = dict.fromkeys(answer_list,after_wd_add_list)#注意
        print('准备填入对象对应子项信息',compound_dict)
#查询对象并填充信息------------------------------------------------------------------------------------------------------        
       
        for rcc ,rkk in enumerate(ref_dir_list):      
            r_value_flag = hasattr(eval(t_obj),rkk)

    
            if r_value_flag:
       
               getattr(eval(t_obj)(),rkk)(compound_dict)   

#---------------------------------------------------------------------------------------------------
#**************************************************************************************************
def 达标_元素():
      
    global tow_to_five_list
    global d_okw_class_list
    global dy_label
    global key_word_label
    global d_okw_class_list
    global tow_to_five_label
    global first_to_five_label
    global first_to_five_list
    global key_word_list_content
    global ot_label
    global o_label_exit_flag
    global k_symbol_flag
    
    global model_label
    global model_kw

    global model_kw_label_flag
    global model_kw_list
    global model_kw_label
    global ignore_kw_label
    global o_kw_label_flag
    global dy_kw_model_dict
    
    global unidentified_word
    global unidentified_flag
    global unidentified_loc

    global smodel_kw_sum
    global smodel_kw_list
    global smodel_kw_label
    
    global model_kw

    global key_word_list
    global first_kw_flag
    global info_word_loc_list
    global fill_kw_loc
    global d_class_list
    global ref_sub_flag
    global p_e_flag
    global s_p_exist_flag
    global conversion_person
    global conversion_usr_info
    global storage_usr_info
    global preset_why
    global compen_label_flag
    global tow_to_five_exit_flag
    global model_exit_flag
    global smodel_exit_flag
    
    fill_kw_loc_list = []
    fill_min_loc = 0
    fill_max_loc = 0
    
    fill_wd_add_list   = ''
    before_wd_add_list = ''
    after_wd_add_list  = ''
    
    fill_wd_list = []
    before_wd_list = []
    after_wd_list = []
    before_kw_len = 0
    after_kw_len = 0
    kw_list_all_len = len(info_word_loc_list) - 1

    methods = []
    attribute = []
    obj = []
    ref_dir_list = ['方法','理由','原因','条件','技能']
    cause = '原因'

    seer_array = ''
    seer_list = []
    r_list_content = []
    match_key_list = []
    
    ref_sub_kw = ''
    dir_list = '大纲'
    t_obj = ''
    t_obj_len = 0
    t_obj_loc = 0
    answer_obj = ''
    answer_obj_len = 0
    answer_obj_loc = 0
    fill_flag = False
    t_obj_list = ''
    r_obj = ''
    c_obj = ''
    t_r_value = []
    default_obj = []
    answer_list = []
    r_value_flag = False
    compound_dict = {}
    
#---------------------------------------------------------------------------------------------------    
    print('☀☀☀☀模型分析 --->>>>>> 达标_元素',model_kw)
    fill_flag = False
    fill_max_loc = max(fill_kw_loc)
    fill_min_loc = min(fill_kw_loc)
#---------------------------------------------------------------------------------------------------
    if p_e_flag:
       t_obj = conversion_person  
       print('✪✪✪✪确定对象',t_obj)
       
    elif first_kw_flag:
         t_obj = key_word_list[0]
         print('❤❤❤❤确定对象',t_obj,key_word_list)
         
    elif tow_to_five_list:
         for ttc,ttk in enumerate(tow_to_five_list):
             r_value_flag = hasattr(eval(ttk),c_obj)
             if r_value_flag:
                t_r_value = getattr(eval(ttk)(),c_obj)()
                t_obj = t_r_value[0]
                print('♔♔♔♔确定对象:',t_obj)
#---------------------------------------------------------------------------------------------------
    if tow_to_five_label and ref_sub_flag == False:

         for tc,tk in enumerate(tow_to_five_label):
             #print('看这里',tk)  
             r_value_flag = hasattr(eval(t_obj),tk)#检测对象是否存在对应子项
             if r_value_flag:
                ref_sub_kw = tk#此处限定其它关键字总数为一个
                ref_dir_list.append(ref_sub_kw)
                ref_sub_flag = True
         print('▓▓▓▓检测',ref_sub_kw)
         

    if smodel_kw_label and ref_sub_flag == False:

         for sc,sk in enumerate(smodel_kw_label):
             print('看这里',sk)  
             r_value_flag = hasattr(eval(t_obj),sk)#检测对象是否存在对应子项
             if r_value_flag:
                ref_sub_kw = sk#此处限定其它关键字总数为一个
                ref_dir_list.append(ref_sub_kw)
                ref_sub_flag = True 

         print('♦♦♦♦检测',ref_sub_kw)
     

    if key_word_label and ref_sub_flag == False:

       for kc,kk in enumerate(smodel_kw_label):
             #print('看这里',kk)  
             r_value_flag = hasattr(eval(t_obj),kk)#检测对象是否存在对应子项
             if r_value_flag:
                ref_sub_kw = kk#此处限定其它关键字总数为一个
                ref_dir_list.append(ref_sub_kw)
                ref_sub_flag = True    
    
       print('〓〓〓〓检测',ref_sub_kw)
    
         
    if ref_sub_flag == False:
       ref_sub_kw = '属性'   
       print('☎☎☎☎没有对应子项填入默认项',ref_sub_flag)
#---------------------------------------------------------------------------------------------------
    if fill_min_loc > 0:
          
       while before_kw_len < fill_min_loc:
             
             before_wd_list.append(info_word_loc_list[before_kw_len])
             before_wd_add_list += info_word_loc_list[before_kw_len]             
             before_kw_len += 1
             print('开始查询前移字符并连接',before_wd_list,before_wd_add_list)
                          
    before_wd_add_list += model_kw[0] #链接模型关键字        
    answer_list.append(before_wd_add_list)
#---------------------------------------------------------------------------------------------------
  
#---------------------------------------------------------------------------------------------------
    #fill_flag = False
    fill_max_loc = max(fill_kw_loc)
    
    if fill_max_loc < kw_list_all_len:
          
       while fill_max_loc < kw_list_all_len:
             fill_max_loc += 1
             after_wd_list.append(info_word_loc_list[fill_max_loc])
             after_wd_add_list += info_word_loc_list[fill_max_loc]
             print('开始查询后移字符并连接',after_wd_list,after_wd_add_list)
             
    #after_wd_add_list = model_kw[0] + after_wd_add_list #链接模型关键字       
#----------------------------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#合成新子项填充信息---------------------------------------------------------------------------------------------------

    #print('☯☯☯☯检测',answer_list)   
    compound_dict = dict.fromkeys(answer_list,after_wd_add_list)#注意
    print('准备填入对象对应子项信息',compound_dict)
#查询对象并填充信息------------------------------------------------------------------------------------------------------        
       
    for rcc ,rkk in enumerate(ref_dir_list):      
        r_value_flag = hasattr(eval(t_obj),rkk)

    
        if r_value_flag:
       
           getattr(eval(t_obj)(),rkk)(compound_dict)
#分析预测形成原因子项信息---------------------------------------------------------------------------          
#**************************************************************************************************
def 查询_原因():
      
    global tow_to_five_list
    global d_okw_class_list
    global dy_label
    global key_word_label
    global d_okw_class_list
    global tow_to_five_label
    global first_to_five_label
    global first_to_five_list
    global key_word_list_content
    global ot_label
    global o_label_exit_flag
    global k_symbol_flag
    
    global model_label
    global model_kw

    global model_kw_label_flag
    global model_kw_list
    global model_kw_label
    global ignore_kw_label
    global o_kw_label_flag
    global dy_kw_model_dict
    
    global unidentified_word
    global unidentified_flag
    global unidentified_loc

    global smodel_kw_sum
    global smodel_kw_list
    global smodel_kw_label
    
    global model_kw

    global key_word_list
    global first_kw_flag
    global info_word_loc_list
    global fill_kw_loc
    global d_class_list
    global ref_sub_flag
    global p_e_flag
    global s_p_exist_flag
    global conversion_person
    global conversion_usr_info
    global storage_usr_info
    global preset_why
    
    fill_kw_loc_list = []
    fill_min_loc = 0
    fill_max_loc = 0
    
    fill_wd_add_list   = ''
    before_wd_add_list = ''
    after_wd_add_list  = ''
    
    fill_wd_list = []
    before_wd_list = []
    after_wd_list = []
    before_kw_len = 0
    after_kw_len = 0
    kw_list_all_len = len(info_word_loc_list) - 1

    methods = []
    attribute = []
    obj = []
    ref_dir_list = ['方法','属性','理由','条件']
    exclusive_kw = '原因'
    exc_answer_list = ['因为要','因为想','因为有']

    seer_array = ''
    seer_list = []
    r_list_content = []
    match_key_list = []
    
    ref_sub_kw = ''
    r_answer = ''
    dir_list = '大纲'
    t_obj = ''
    t_obj_len = 0
    t_obj_loc = 0
    answer_obj = ''
    answer_obj_len = 0
    answer_obj_loc = 0
    fill_flag = False
    t_obj_list = ''
    r_obj = ''
    c_obj = ''
    t_r_value = []
    default_obj = []
    answer_list = []
    r_value_flag = False
    compound_dict = {}
    
#---------------------------------------------------------------------------------------------------    
    print('☀☀☀☀模型分析 --->>>>>> 查询_原因',model_kw)
    fill_flag = False
    fill_max_loc = max(fill_kw_loc)
    fill_min_loc = min(fill_kw_loc)
#---------------------------------------------------------------------------------------------------
    if fill_min_loc > 0:
          
       while before_kw_len < fill_min_loc:
             
             before_wd_list.append(info_word_loc_list[before_kw_len])
             before_wd_add_list += info_word_loc_list[before_kw_len]
             print('开始查询前移字符并连接',before_wd_list,before_wd_add_list)
             before_kw_len += 1
             
    #before_wd_add_list += model_kw[0] #链接模型关键字        
    #answer_list.append(before_wd_add_list)
#---------------------------------------------------------------------------------------------------
    #fill_flag = False
    fill_max_loc = max(fill_kw_loc)
    
    if fill_max_loc < kw_list_all_len:
          
       while fill_max_loc < kw_list_all_len:
             fill_max_loc += 1
             after_wd_list.append(info_word_loc_list[fill_max_loc])
             after_wd_add_list += info_word_loc_list[fill_max_loc]
             print('开始查询后移字符并连接',after_wd_list,after_wd_add_list)
             
    #after_wd_add_list = model_kw[0] + after_wd_add_list #链接模型关键字       
#--------------------------------------------------------------------------------------------------
    if after_wd_add_list:
       print('❁❁❁❁确定查询关键字:',after_wd_add_list)
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#确定对象

    if before_wd_add_list:
       t_obj = before_wd_add_list
       print('☯☯☯☯确定对象:',before_wd_add_list)
       
    elif p_e_flag:
       t_obj = conversion_person  
       print('◪◪◪◪确定对象:',t_obj)
       
    elif key_word_list:
         t_obj = key_word_list[0]
         print('◮◮◮◮确定对象:',t_obj)
         
    elif tow_to_five_list:
         t_obj = tow_to_five_list[0]
         print('◕◕◕◕确定对象:',t_obj)

#---------------------------------------------------------------------------------------------------
    for rcc ,rkk in enumerate(ref_dir_list):      
        r_answer = getattr(eval(t_obj)(),exclusive_kw)(after_wd_add_list)
        
    print('☁☁☁☁答案:',exc_answer_list[0] + r_answer)
    
        #if r_value_flag:
       
           #getattr(eval(t_obj)(),rkk)(compound_dict)
#**************************************************************************************************
def 判断_行为():
      
    global tow_to_five_list
    global d_okw_class_list
    global dy_label
    global key_word_label
    global d_okw_class_list
    global tow_to_five_label
    global first_to_five_label
    global first_to_five_list
    global key_word_list_content
    global ot_label
    global o_label_exit_flag
    global k_symbol_flag
    
    global model_label
    global model_kw

    global model_kw_label_flag
    global model_kw_list
    global model_kw_label
    global ignore_kw_label
    global o_kw_label_flag
    global dy_kw_model_dict
    
    global unidentified_word
    global unidentified_flag
    global unidentified_loc
    
    global model_kw

    global key_word_list
    global first_kw_flag
    global info_word_loc_list
    global fill_kw_loc
    global d_class_list
    global ref_sub_flag
    global p_e_flag
    global s_p_exist_flag
    global conversion_person
    global conversion_usr_info

    global smodel_kw_sum
    global smodel_kw_list
    global smodel_kw_label

    global map_table
    global gc_back_wd
    global gc_obj
    global map_flag
    global f_result_flag
    
    fill_kw_loc_list = []
    fill_min_loc = 0
    fill_max_loc = 0
    
    fill_wd_add_list   = ''
    before_wd_add_list = ''
    after_wd_add_list  = ''
    
    fill_wd_list = []
    before_wd_list = []
    after_wd_list = []
    before_kw_len = 0
    after_kw_len = 0
    kw_list_all_len = len(info_word_loc_list) - 1

    methods = []
    attribute = []
    obj = []

    r_list_content = []
    match_key_list = []

    ref_dir_list = []
    
    ref_sub_kw = ''
    dir_list = '大纲'
    t_obj = ''
    t_obj_len = 0
    t_obj_loc = 0
    answer_obj = ''
    answer_obj_len = 0
    answer_obj_loc = 0
    fill_flag = False
    t_obj_list = ''
    r_obj = ''
    c_obj = '对象'
    t_r_value = []
    default_obj = []
    answer_list = []
    r_value_flag = False
    type_judge = False
    type_value = False
    compound_dict = {}
    back_wd = ''
    r_map_obj = ''

#---------------------------------------------------------------------------------------------------    
    print('☀☀☀☀模型分析 --->>>>>> 判断_行为',model_kw)
    fill_flag = False
    fill_max_loc = max(fill_kw_loc)
    fill_min_loc = min(fill_kw_loc)
#---------------------------------------------------------------------------------------------------
    if fill_min_loc > 0:
          
       while before_kw_len < fill_min_loc:
             
             before_wd_list.append(info_word_loc_list[before_kw_len])
             before_wd_add_list += info_word_loc_list[before_kw_len]
             print('开始查询前移字符并连接',before_wd_list,before_wd_add_list)
             before_kw_len += 1
             
    before_wd_add_list += model_kw[0] #链接模型关键字        
    answer_list.append(before_wd_add_list)
    print('◤◤◤◤前移连接后字符信息:',before_wd_add_list)
#---------------------------------------------------------------------------------------------------
    #fill_flag = False
    fill_max_loc = max(fill_kw_loc)
    
    if fill_max_loc < kw_list_all_len:
          
       while fill_max_loc < kw_list_all_len:
             fill_max_loc += 1
             after_wd_list.append(info_word_loc_list[fill_max_loc])
             after_wd_add_list += info_word_loc_list[fill_max_loc]
             print('开始查询后移字符并连接',after_wd_list,after_wd_add_list)
             
    #after_wd_add_list = model_kw[1] + after_wd_add_list #链接模型关键字
    print('◥◥◥◥后移连接后字符信息:',after_wd_add_list,tow_to_five_list)
#--------------------------------------------------------------------------------------------------
    if p_e_flag:
       t_obj = conversion_person  
       print('✪✪✪✪确定对象',t_obj)
       
    elif first_kw_flag:
         t_obj = key_word_list[0]
         print('❤❤❤❤确定对象',t_obj,key_word_list)
         
    elif tow_to_five_list:
         for ttc,ttk in enumerate(tow_to_five_list):
             r_value_flag = hasattr(eval(ttk),c_obj)
             if r_value_flag:
                t_r_value = getattr(eval(ttk)(),c_obj)()
                t_obj = t_r_value[0]
                print('♔♔♔♔确定对象:',t_obj)
#--------------------------------------------------------------------------------------------------
    print('☯☯☯☯检测',answer_list)   
    compound_dict = dict.fromkeys(answer_list,after_wd_add_list)#注意
    print('准备填入对象对应子项信息',compound_dict)
#--------------------------------------------------------------------------------------------------
    if tow_to_five_label and ref_sub_flag == False:

         for tc,tk in enumerate(tow_to_five_label):
             #print('看这里',tk)  
             r_value_flag = hasattr(eval(t_obj),tk)#检测对象是否存在对应子项
             if r_value_flag:
                ref_sub_kw = tk#此处限定其它关键字总数为一个
                ref_dir_list.append(ref_sub_kw)
                ref_sub_flag = True
         print('▓▓▓▓检测',ref_sub_kw)
         

    if smodel_kw_label and ref_sub_flag == False:

         for sc,sk in enumerate(smodel_kw_label):
             print('看这里',sk)  
             r_value_flag = hasattr(eval(t_obj),sk)#检测对象是否存在对应子项
             if r_value_flag:
                ref_sub_kw = sk#此处限定其它关键字总数为一个
                ref_dir_list.append(ref_sub_kw)
                ref_sub_flag = True 

         print('♦♦♦♦检测',ref_sub_kw)
     

    if key_word_label and ref_sub_flag == False:

       for kc,kk in enumerate(smodel_kw_label):
             #print('看这里',kk)  
             r_value_flag = hasattr(eval(t_obj),kk)#检测对象是否存在对应子项
             if r_value_flag:
                ref_sub_kw = kk#此处限定其它关键字总数为一个
                ref_dir_list.append(ref_sub_kw)
                ref_sub_flag = True    
    
       print('〓〓〓〓检测',ref_sub_kw)
    
         
    if ref_sub_flag == False:
       ref_sub_kw = '属性'   
       print('☎☎☎☎没有对应子项填入默认项',ref_sub_flag)
#向对象填入对应子项信息-----------------------------------------------------------------------------
    if model_exit_flag and k_symbol_flag:#判断语句性质(学习/询问/倾诉)

       for rcc ,rkk in enumerate(ref_dir_list):      
           r_value_flag = hasattr(eval(t_obj),rkk)    
           if r_value_flag:
       
              getattr(eval(t_obj)(),rkk)(compound_dict)

    else: #t_obj ref_sub_kw before_wd_add_list after_wd_add_list back_wd
        r_obj = acquire_resule(t_obj,ref_sub_kw,before_wd_add_list,after_wd_add_list)
        if r_obj:
           print('☁☁☁☁获取答案:',r_obj)
        else:
           print('☡☡☡☡获取答案失败:',r_obj)
 
#---------------------------------------------------------------------------------------------------

#**************************************************************************************************
def 条件_应该():
      
    global tow_to_five_list
    global d_okw_class_list
    global dy_label
    global key_word_label
    global d_okw_class_list
    global tow_to_five_label
    global first_to_five_label
    global first_to_five_list
    global key_word_list_content
    global ot_label
    global o_label_exit_flag
    global k_symbol_flag
    
    global model_label
    global model_kw

    global model_kw_label_flag
    global model_kw_list
    global model_kw_label
    global ignore_kw_label
    global o_kw_label_flag
    global dy_kw_model_dict
    
    global unidentified_word
    global unidentified_flag
    global unidentified_loc
    
    global model_kw

    global key_word_list
    global first_kw_flag
    global info_word_loc_list
    global fill_kw_loc
    global d_class_list
    global ref_sub_flag
    global p_e_flag
    global s_p_exist_flag
    global conversion_person
    global conversion_usr_info

    global smodel_kw_sum
    global smodel_kw_list
    global smodel_kw_label
    
    fill_kw_loc_list = []
    fill_min_loc = 0
    fill_max_loc = 0
    
    fill_wd_add_list   = ''
    before_wd_add_list = ''
    after_wd_add_list  = ''
    
    fill_wd_list = []
    before_wd_list = []
    after_wd_list = []
    before_kw_len = 0
    after_kw_len = 0
    kw_list_all_len = len(info_word_loc_list) - 1

    methods = []
    attribute = []
    obj = []

    r_list_content = []
    match_key_list = []

    ref_dir_list = []
    
    #ref_sub_kw = '情绪'
    dir_list = '大纲'
    t_obj = ''
    t_obj_len = 0
    t_obj_loc = 0
    answer_obj = ''
    answer_obj_len = 0
    answer_obj_loc = 0
    fill_flag = False
    t_obj_list = ''
    r_obj = ''
    c_obj = '对象'
    t_r_value = []
    default_obj = []
    answer_list = []
    r_value_flag = False
    compound_dict = {}
    
#---------------------------------------------------------------------------------------------------    
    print('☀☀☀☀模型分析 --->>>>>> 条件_应该',model_kw)
    fill_flag = False
    fill_max_loc = max(fill_kw_loc)
    fill_min_loc = min(fill_kw_loc)
#---------------------------------------------------------------------------------------------------
    if fill_min_loc > 0:
          
       while before_kw_len < fill_min_loc:
             
             before_wd_list.append(info_word_loc_list[before_kw_len])
             before_wd_add_list += info_word_loc_list[before_kw_len]
             print('开始查询前移字符并连接',before_wd_list,before_wd_add_list)
             before_kw_len += 1
             
    before_wd_add_list += model_kw[0] #链接模型关键字        
    answer_list.append(before_wd_add_list)
    print('◤◤◤◤前移连接后字符信息:',before_wd_add_list)
#---------------------------------------------------------------------------------------------------
    #fill_flag = False
    fill_max_loc = max(fill_kw_loc)
    
    if fill_max_loc < kw_list_all_len:
          
       while fill_max_loc < kw_list_all_len:
             fill_max_loc += 1
             after_wd_list.append(info_word_loc_list[fill_max_loc])
             after_wd_add_list += info_word_loc_list[fill_max_loc]
             print('开始查询后移字符并连接',after_wd_list,after_wd_add_list)
             
    after_wd_add_list = model_kw[1] + after_wd_add_list #链接模型关键字
    print('◥◥◥◥后移连接后字符信息:',after_wd_add_list,tow_to_five_list)
#--------------------------------------------------------------------------------------------------
    if p_e_flag:
       t_obj = conversion_person  
       print('✪✪✪✪确定对象',t_obj)
       
    elif first_kw_flag:
         t_obj = key_word_list[0]
         print('❤❤❤❤确定对象',t_obj,key_word_list)
         
    elif tow_to_five_list:
         for ttc,ttk in enumerate(tow_to_five_list):
             r_value_flag = hasattr(eval(ttk),c_obj)
             if r_value_flag:
                t_r_value = getattr(eval(ttk)(),c_obj)()
                t_obj = t_r_value[0]
                print('♔♔♔♔确定对象:',t_obj)
#--------------------------------------------------------------------------------------------------
    print('☯☯☯☯检测',answer_list)   
    compound_dict = dict.fromkeys(answer_list,after_wd_add_list)#注意
    print('准备填入对象对应子项信息',compound_dict)
#--------------------------------------------------------------------------------------------------
    if tow_to_five_label and ref_sub_flag == False:

         for tc,tk in enumerate(tow_to_five_label):
             #print('看这里',tk)  
             r_value_flag = hasattr(eval(t_obj),tk)#检测对象是否存在对应子项
             if r_value_flag:
                ref_sub_kw = tk#此处限定其它关键字总数为一个
                ref_dir_list.append(ref_sub_kw)
                ref_sub_flag = True
         print('▓▓▓▓检测',ref_sub_kw)
         

    if smodel_kw_label and ref_sub_flag == False:

         for sc,sk in enumerate(smodel_kw_label):
             print('看这里',sk)  
             r_value_flag = hasattr(eval(t_obj),sk)#检测对象是否存在对应子项
             if r_value_flag:
                ref_sub_kw = sk#此处限定其它关键字总数为一个
                ref_dir_list.append(ref_sub_kw)
                ref_sub_flag = True 

         print('♦♦♦♦检测',ref_sub_kw)
     

    if key_word_label and ref_sub_flag == False:

       for kc,kk in enumerate(smodel_kw_label):
             #print('看这里',kk)  
             r_value_flag = hasattr(eval(t_obj),kk)#检测对象是否存在对应子项
             if r_value_flag:
                ref_sub_kw = kk#此处限定其它关键字总数为一个
                ref_dir_list.append(ref_sub_kw)
                ref_sub_flag = True    
    
       print('〓〓〓〓检测',ref_sub_kw)
    
         
    if ref_sub_flag == False:
       ref_sub_kw = '属性'   
       print('☎☎☎☎没有对应子项填入默认项',ref_sub_flag)
#向对象填入对应子项信息-----------------------------------------------------------------------------
    for rcc ,rkk in enumerate(ref_dir_list):      
            r_value_flag = hasattr(eval(t_obj),rkk)

    
            if r_value_flag:
       
               getattr(eval(t_obj)(),rkk)(compound_dict) 
#**************************************************************************************************
def 属性_指示():
      
    global tow_to_five_list
    global d_okw_class_list
    global dy_label
    global key_word_label
    global d_okw_class_list
    global tow_to_five_label
    global first_to_five_label
    global first_to_five_list
    global key_word_list_content
    global ot_label
    global o_label_exit_flag
    global k_symbol_flag
    
    global model_label
    global model_kw

    global model_kw_label_flag
    global model_kw_list
    global model_kw_label
    global ignore_kw_label
    global o_kw_label_flag
    global dy_kw_model_dict
    
    global unidentified_word
    global unidentified_flag
    global unidentified_loc
    
    global model_kw

    global key_word_list
    global first_kw_flag
    global info_word_loc_list
    global fill_kw_loc
    global d_class_list
    global ref_sub_flag
    global p_e_flag
    global s_p_exist_flag
    global conversion_person
    global conversion_usr_info

    global smodel_kw_sum
    global smodel_kw_list
    global smodel_kw_label
    
    fill_kw_loc_list = []
    fill_min_loc = 0
    fill_max_loc = 0
    
    fill_wd_add_list   = ''
    before_wd_add_list = ''
    after_wd_add_list  = ''
    
    fill_wd_list = []
    before_wd_list = []
    after_wd_list = []
    before_kw_len = 0
    after_kw_len = 0
    kw_list_all_len = len(info_word_loc_list) - 1

    methods = []
    attribute = []
    obj = []
    
    r_list_content = []
    match_key_list = []
    
    ref_sub_kw = ''
    dir_list = '大纲'
    t_obj = ''
    t_obj_len = 0
    t_obj_loc = 0
    answer_obj = ''
    answer_obj_len = 0
    answer_obj_loc = 0
    fill_flag = False
    t_obj_list = ''
    r_obj = ''
    c_obj = ''
    t_r_value = []
    default_obj = []
    answer_list = []
    r_value_flag = False
    compound_dict = {}
    
#---------------------------------------------------------------------------------------------------    
    print('☀☀☀☀模型分析 --->>>>>> 属性_指示',model_kw)
    fill_flag = False
    fill_max_loc = max(fill_kw_loc)
    fill_min_loc = min(fill_kw_loc)
#---------------------------------------------------------------------------------------------------
    if fill_min_loc > 0:
          
       while before_kw_len < fill_min_loc:
             
             before_wd_list.append(info_word_loc_list[before_kw_len])
             before_wd_add_list += info_word_loc_list[before_kw_len]
             print('开始查询前移字符并连接',before_wd_list,before_wd_add_list)
             before_kw_len += 1
             
    before_wd_add_list += model_kw[0] #链接模型关键字        
    answer_list.append(before_wd_add_list)
#---------------------------------------------------------------------------------------------------
    #fill_flag = False
    fill_max_loc = max(fill_kw_loc)
    
    if fill_max_loc < kw_list_all_len:
          
       while fill_max_loc < kw_list_all_len:
             fill_max_loc += 1
             after_wd_list.append(info_word_loc_list[fill_max_loc])
             after_wd_add_list += info_word_loc_list[fill_max_loc]
             print('开始查询后移字符并连接',after_wd_list,after_wd_add_list)
             
    #after_wd_add_list = model_kw[0] + after_wd_add_list #链接模型关键字       
#--------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
    #确定对象
    if p_e_flag:
       t_obj = conversion_person  
       print('确定对象',t_obj)
       
    elif key_word_list:
         t_obj = key_word_list[0]
         print('确定对象',t_obj)
    elif tow_to_five_list:
         t_obj = tow_to_five_list[0]
         print('确定对象',t_obj)

#---------------------------------------------------------------------------------------------------
    
    for dyc,ddk in enumerate(dy_kw_model_dict):
           for dyk,dyv in ddk.items():
               if dyk == '对象':            
                  dyv.append(before_wd_add_list)
                
    print('✔✔✔✔更新对应子项信息',dy_kw_model_dict)
#合成新子项填充信息---------------------------------------------------------------------------------------------------

    print('☯☯☯☯检测',answer_list)   
    compound_dict = dict.fromkeys(answer_list,after_wd_add_list)#注意
    print('准备填入对象对应子项信息',compound_dict)
#查询对象并填充信息------------------------------------------------------------------------------------------------------    
    

    if tow_to_five_label:
         for  ttc,ttk in enumerate(tow_to_five_label):
              r_value_flag = hasattr(eval(t_obj),ttk)
              if r_value_flag:
                 ref_sub_kw = ttk#tow_to_five_label[0]#此处限定其它关键字总数为一个
                 print('▓▓▓▓检测',ref_sub_kw)
                 ref_sub_flag = True

    if smodel_kw_label:
       for  stc,stk in enumerate(smodel_kw_label):
            r_value_flag = hasattr(eval(t_obj),stk)
            if r_value_flag:
               ref_sub_kw = stk#tow_to_five_label[0]#此处限定其它关键字总数为一个
               print('♞♞♞♞检测',ref_sub_kw)
               ref_sub_flag = True           

    elif key_word_label:
       ref_sub_kw = key_word_label[0]#此处限定第一关键字总数为一个
       print('〓〓〓〓检测',ref_sub_kw)
       ref_sub_flag = True     
         
    if ref_sub_flag == False:
       ref_sub_kw = '属性'   
       print('☎☎☎☎没有对应子项填入默认项',ref_sub_flag)
       
    r_value_flag = hasattr(eval(t_obj),ref_sub_kw)
    
    if r_value_flag:
       getattr(eval(t_obj)(),ref_sub_kw)(compound_dict)

    else:
       ref_sub_kw = '属性'
    
       getattr(eval(t_obj)(),ref_sub_kw)(compound_dict)
    #or rcc,rkk in enumerate(r_list_content):
#///////////////////////////////////////////////////////////////////////////////////////////////////
def 差异_识别():
      
    global tow_to_five_list
    global d_okw_class_list
    global dy_label
    global key_word_label
    global d_okw_class_list
    global tow_to_five_label
    global first_to_five_label
    global first_to_five_list
    global key_word_list_content
    global ot_label
    global o_label_exit_flag
    global k_symbol_flag
    
    global model_label
    global model_kw

    global model_kw_label_flag
    global model_kw_list
    global model_kw_label
    global ignore_kw_label
    global o_kw_label_flag
    global dy_kw_model_dict
    
    global unidentified_word
    global unidentified_flag
    global unidentified_loc
    
    global model_kw

    global key_word_list
    global first_kw_flag
    global info_word_loc_list
    global fill_kw_loc
    global d_class_list
    global ref_sub_flag
    
    global p_e_flag
    global first_kw_flag
    global s_p_exist_flag
    global conversion_person
    global conversion_usr_info
    global conversion_person

    global smodel_kw_sum
    global smodel_kw_list
    global smodel_kw_label
    global pref_word_none
    
    fill_kw_loc_list = []
    fill_min_loc = 0
    fill_max_loc = 0
    
    fill_wd_add_list   = ''
    before_wd_add_list = ''
    after_wd_add_list  = ''
    
    fill_wd_list = []
    before_wd_list = []
    after_wd_list = []
    before_kw_len = 0
    after_kw_len = 0
    kw_list_all_len = len(info_word_loc_list) - 1

    methods = []
    attribute = []
    obj = []
    
    r_list_content = []
    match_key_list = []
    
    ref_sub_kw = ''
    dir_list = '大纲'
    t_obj = ''
    t_obj_len = 0
    t_obj_loc = 0
    answer_obj = ''
    answer_obj_len = 0
    answer_obj_loc = 0
    fill_flag = False
    t_obj_list = ''
    r_obj = ''
    c_obj = ''
    t_r_value = []
    default_obj = []
    answer_list = []
    r_value_flag = False
    ref_kw_flag = False
    compound_dict = {}
    t_judge = False#isinstance(parameter, str)
    preset_wd = '你木有告诉我哦'
    
#---------------------------------------------------------------------------------------------------    
    print('☀☀☀☀模型分析 --->>>>>> 差异_识别',model_kw)
    print('§§§§检测关键元素',conversion_person,conversion_usr_info,key_word_list,tow_to_five_list)

    if s_p_exist_flag:
       print('查看',s_p_exist_flag)   
       for cc,ck in enumerate(conversion_usr_info):             
           default_obj.append(ck)
           
    elif p_e_flag:
         print('查看',s_p_exist_flag) 
         default_obj.append(conversion_person)
         
         print('♧♧♧♧查询人称元素',default_obj)

    if first_kw_flag:
       for kc,kk in enumerate(key_word_list):
             
           default_obj.append(kk)
           
    print('♧♧♧♧查询第一关键字元素',match_key_list)

    if tow_to_five_list:
       for tc,tk in enumerate(tow_to_five_list):
             
           attribute.append(tk)       
           
    print('♧♧♧♧查询二至七关键字元素',attribute)

    if smodel_kw_list:
       ref_kw_flag = True   
       for tc,tk in enumerate(smodel_kw_list):
           answer_list.append(tk)           
       ref_sub_kw = answer_list[0]
       
    print('❀❀❀❀查询可能成为参考标签列表',ref_sub_kw,ref_kw_flag)
    
    print('❉❉❉❉对象列表',default_obj)

#--------------------------------------------------------------------------------------------------
    for doc,dok in enumerate(default_obj):
        r_value_flag = hasattr(eval(dok),ref_sub_kw)
        if r_value_flag:
           t_r_values = getattr(eval(dok)(),ref_sub_kw)(ref_sub_kw)
           t_judge = isinstance(t_r_values, str)
           if t_judge:  
              pass#注意,后续代码需补充
            
           else:
              methods.append(dok + ref_sub_kw + preset_wd )
              r_obj = methods
              r_obj = ''.join(r_obj)
              print('看连接项信息',r_obj)
        else:
           print('◆◆◆◆注意',dok + pref_word_none + ref_sub_kw + '-->>子项')   
           methods.append(dok + pref_word_none + ref_sub_kw)
           c_obj = methods
           c_obj = ''.join(c_obj)
           #print(dok + pref_word_none + ref_sub_kw)
    #print(r_obj)       
#--------------------------------------------------------------------------------------------------    

#///////////////////////////////////////////////////////////////////////////////////////////////////
def 位置_指示():
      
    global tow_to_five_list
    global d_okw_class_list
    global dy_label
    global key_word_label
    global d_okw_class_list
    global tow_to_five_label
    global first_to_five_label
    global first_to_five_list
    global key_word_list_content
    global ot_label
    global o_label_exit_flag
    global k_symbol_flag
    
    global model_label
    global model_kw

    global model_kw_label_flag
    global model_kw_list
    global model_kw_label
    global ignore_kw_label
    global o_kw_label_flag
    global dy_kw_model_dict
    
    global unidentified_word
    global unidentified_flag
    global unidentified_loc
    
    global model_kw

    global key_word_list
    global first_kw_flag
    global info_word_loc_list
    global fill_kw_loc
    global d_class_list
    global ref_sub_flag
    global p_e_flag
    global conversion_person
    
    fill_kw_loc_list = []
    fill_min_loc = 0
    fill_max_loc = 0
    
    fill_wd_add_list   = ''
    before_wd_add_list = ''
    after_wd_add_list  = ''
    
    fill_wd_list = []
    before_wd_list = []
    after_wd_list = []
    before_kw_len = 0
    after_kw_len = 0
    kw_list_all_len = len(info_word_loc_list) - 1

    methods = []
    attribute = []
    obj = []
    
    r_list_content = []
    match_key_list = []
    
    ref_sub_kw = ''
    dir_list = '大纲'
    t_obj = ''
    t_obj_len = 0
    t_obj_loc = 0
    answer_obj = ''
    answer_obj_len = 0
    answer_obj_loc = 0
    fill_flag = False
    t_obj_list = ''
    r_obj = ''
    c_obj = ''
    t_r_value = []
    default_obj = []
    answer_list = []
    r_value_flag = False
    compound_dict = {}
    
#---------------------------------------------------------------------------------------------------    
    print('☀☀☀☀模型分析 --->>>>>> 位置_指示',model_kw)
    fill_flag = False
    fill_max_loc = max(fill_kw_loc)
    fill_min_loc = min(fill_kw_loc)
#---------------------------------------------------------------------------------------------------
    if fill_min_loc > 0:
          
       while before_kw_len < fill_min_loc:
             
             before_wd_list.append(info_word_loc_list[before_kw_len])
             before_wd_add_list += info_word_loc_list[before_kw_len]
             print('开始查询前移字符并连接',before_wd_list,before_wd_add_list)
             before_kw_len += 1
    
#---------------------------------------------------------------------------------------------------
    #fill_flag = False
    fill_max_loc = max(fill_kw_loc)
    
    if fill_max_loc < kw_list_all_len:
          
       while fill_max_loc < kw_list_all_len:
             fill_max_loc += 1
             after_wd_list.append(info_word_loc_list[fill_max_loc])
             after_wd_add_list += info_word_loc_list[fill_max_loc]
             print('开始查询后移字符并连接',after_wd_list,after_wd_add_list)
             
    after_wd_add_list = model_kw[0] + after_wd_add_list #链接模型关键字       
#--------------------------------------------------------------------------------------------------
    for dyc,ddk in enumerate(dy_kw_model_dict):
           for dyk,dyv in ddk.items():
               if dyk == '属性':            
                  dyv.append(after_wd_add_list)
                  
    print('更新对应子项信息',dy_kw_model_dict)
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
    #确定对象
    if p_e_flag:
       t_obj = conversion_person  
       print('确定对象',t_obj)
       
    elif key_word_list:
         t_obj = key_word_list[0]
         print('确定对象',t_obj)
         
    elif tow_to_five_list:
         t_obj = tow_to_five_list[0]
         print('确定对象',t_obj)

#---------------------------------------------------------------------------------------------------
    
    for dyc,ddk in enumerate(dy_kw_model_dict):
           for dyk,dyv in ddk.items():
               if dyk == '对象':            
                  dyv.append(before_wd_add_list)
                
    print('✔✔✔✔更新对应子项信息',dy_kw_model_dict)
#合成新字典---------------------------------------------------------------------------------------------------

    compound_dict = dict.fromkeys(t_obj,after_wd_add_list)
    print('准备填入对象对应子项信息',compound_dict)
#查询对象并填充信息------------------------------------------------------------------------------------------------------    
    

    if tow_to_five_label:
         ref_sub_kw = tow_to_five_label[0]#此处限定其它关键字总数为一个
         print('▓▓▓▓检测',ref_sub_kw)
         ref_sub_flag = True


    elif key_word_label:
       ref_sub_kw = key_word_label[0]#此处限定第一关键字总数为一个
       print('〓〓〓〓检测',ref_sub_kw)
       ref_sub_flag = True     
         
    if ref_sub_flag == False:
       ref_sub_kw = '属性'   
       print('☎☎☎☎没有对应子项填入默认项',ref_sub_flag)
       
    r_value_flag = hasattr(eval(t_obj),ref_sub_kw)
    
    if r_value_flag:
       getattr(eval(t_obj)(),ref_sub_kw)(compound_dict)

    
    else:
       ref_sub_kw = '属性'
       print('!!!!子项检测不存在',r_value_flag)
       getattr(eval(t_obj)(),ref_sub_kw)(compound_dict)       
        
#---------------------------------------------------------------------------------------------------       
def 获得_属性():
      
    global tow_to_five_list
    global d_okw_class_list
    global dy_label
    global key_word_label
    global d_okw_class_list
    global tow_to_five_label
    global first_to_five_label
    global first_to_five_list
    global key_word_list_content
    global ot_label
    global o_label_exit_flag
    global k_symbol_flag
    
    global model_label
    global model_kw

    global model_kw_label_flag
    global model_kw_list
    global model_kw_label
    global ignore_kw_label
    global o_kw_label_flag
    global dy_kw_model_dict
    
    global unidentified_word
    global unidentified_flag
    global unidentified_loc

    global smodel_kw_sum
    global smodel_kw_list
    global smodel_kw_label
    
    global model_kw

    global key_word_list
    global first_kw_flag
    global info_word_loc_list
    global fill_kw_loc
    global d_class_list
    global ref_sub_flag
    global p_e_flag
    global s_p_exist_flag
    global conversion_person
    global conversion_usr_info
    global storage_usr_info
    global preset_why
    global compen_label_flag
    global tow_to_five_exit_flag
    global model_exit_flag
    global smodel_exit_flag
    global k_symbol_flag
    
    fill_kw_loc_list = []
    fill_min_loc = 0
    fill_max_loc = 0
    
    fill_wd_add_list   = ''
    before_wd_add_list = ''
    after_wd_add_list  = ''
    
    fill_wd_list = []
    before_wd_list = []
    after_wd_list = []
    before_kw_len = 0
    after_kw_len = 0
    kw_list_all_len = len(info_word_loc_list) - 1

    methods = []
    attribute = []
    obj = []
    ref_dir_list = ['方法','属性','理由','原因','条件']
    preset_wd = '是'

    seer_array = ''
    seer_list = []
    r_list_content = []
    match_key_list = []
    
    ref_sub_kw = ''
    dir_list = '大纲'
    t_obj = ''
    t_obj_len = 0
    t_obj_loc = 0
    answer_obj = ''
    answer_obj_len = 0
    answer_obj_loc = 0
    fill_flag = False
    t_obj_list = ''
    r_obj = ''
    c_obj = '对象'
    t_r_value = []
    default_obj = []
    answer_list = []
    r_value_flag = False
    obj_sub_flag = False
    compound_dict = {}
    
#---------------------------------------------------------------------------------------------------    
    print('☀☀☀☀模型分析 --->>>>>> 获得_属性',model_kw)
    fill_flag = False
    fill_max_loc = max(fill_kw_loc)
    fill_min_loc = min(fill_kw_loc)

#---------------------------------------------------------------------------------------------------
    #确定对象
    if p_e_flag:
       t_obj = conversion_person  
       print('✪✪✪✪确定对象',t_obj)
       
    elif first_kw_flag:
         t_obj = key_word_list[0]
         print('❤❤❤❤确定对象',t_obj,key_word_list)
         
    elif tow_to_five_list:
         for ttc,ttk in enumerate(tow_to_five_list):
             r_value_flag = hasattr(eval(ttk),c_obj)
             if r_value_flag:
                t_r_value = getattr(eval(ttk)(),c_obj)()
                t_obj = t_r_value[0]
                print('♔♔♔♔确定对象:',t_obj)
#---------------------------------------------------------------------------------------------------
    if tow_to_five_label and ref_sub_flag == False:

         for tc,tk in enumerate(tow_to_five_label):
             print('看这里',tk)  
             r_value_flag = hasattr(eval(t_obj),tk)#检测对象是否存在对应子项
             if r_value_flag:
                ref_sub_kw = tk#此处限定其它关键字总数为一个
                ref_dir_list.append(ref_sub_kw)
                ref_sub_flag = True
         print('▓▓▓▓检测',ref_sub_kw)
         

    if smodel_kw_label and ref_sub_flag == False:

         for sc,sk in enumerate(smodel_kw_label):
             print('看这里',sk)  
             r_value_flag = hasattr(eval(t_obj),sk)#检测对象是否存在对应子项
             if r_value_flag:
                ref_sub_kw = sk#此处限定其它关键字总数为一个
                ref_dir_list.append(ref_sub_kw)
                ref_sub_flag = True 

         print('♦♦♦♦检测',ref_sub_kw)
     

    if key_word_label and ref_sub_flag == False:

       for kc,kk in enumerate(smodel_kw_label):
             print('看这里',kk)  
             r_value_flag = hasattr(eval(t_obj),kk)#检测对象是否存在对应子项
             if r_value_flag:
                ref_sub_kw = kk#此处限定其它关键字总数为一个
                ref_dir_list.append(ref_sub_kw)
                ref_sub_flag = True    
    
       print('〓〓〓〓检测',ref_sub_kw)
    
         
    if ref_sub_flag == False:
       ref_sub_kw = '对象'   
       print('☎☎☎☎没有对应子项填入默认项',ref_sub_kw)
#---------------------------------------------------------------------------------------------------
    if fill_min_loc > 0:
          
       while before_kw_len < fill_min_loc:
             
             before_wd_list.append(info_word_loc_list[before_kw_len])
             before_wd_add_list += info_word_loc_list[before_kw_len]             
             before_kw_len += 1
             print('开始查询前移字符并连接',before_wd_list,before_wd_add_list)
                          
    #before_wd_add_list += model_kw[0] #链接模型关键字        
    answer_list.append(before_wd_add_list)
#---------------------------------------------------------------------------------------------------
    #while fill_min_loc < fill_max_loc:
          #fill_min_loc += 1
          #fill_wd_list.append(info_word_loc_list[fill_min_loc])
          #fill_wd_add_list = fill_wd_add_list + info_word_loc_list[fill_min_loc]
          #print('开始填充并连接',fill_wd_list,fill_wd_add_list)
    #print('查看插入填充子项信息',dy_kw_model_dict) 
#---------------------------------------------------------------------------------------------------
    #fill_flag = False
    fill_max_loc = max(fill_kw_loc)
    
    if fill_max_loc < kw_list_all_len:
          
       while fill_max_loc < kw_list_all_len:
             fill_max_loc += 1
             after_wd_list.append(info_word_loc_list[fill_max_loc])
             after_wd_add_list += info_word_loc_list[fill_max_loc]
             print('开始查询后移字符并连接',after_wd_list,after_wd_add_list)
             
    after_wd_add_list = model_kw[0] + after_wd_add_list #链接模型关键字       
#----------------------------------------------------------------------------------------------------    
#----------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

#合成新子项填充信息---------------------------------------------------------------------------------------------------

    if k_symbol_flag:
       r_value_flag = hasattr(eval(t_obj),ref_sub_kw)
       if r_value_flag:
          print('✔✔✔✔对象存在对应子项:',ref_sub_kw)    
          seer_array =  getattr(eval(t_obj)(),ref_sub_kw)(before_wd_add_list)
          print('☁☁☁☁获取答案:',t_obj + preset_wd + seer_array)
       else:
          print('✘✘✘✘对象没有对应子项:',ref_sub_kw)   
       
    else:
        print('☯☯☯☯检测',answer_list)   
        compound_dict = dict.fromkeys(answer_list,after_wd_add_list)#注意
        print('准备填入对象对应子项信息',compound_dict)
#查询对象并填充信息------------------------------------------------------------------------------------------------------        
       
        for rcc ,rkk in enumerate(ref_dir_list):      
            r_value_flag = hasattr(eval(t_obj),rkk)

    
            if r_value_flag:
       
               getattr(eval(t_obj)(),rkk)(compound_dict)
#///////////////////////////////////////////////////////////////////////////////////////////////////
def 条件_警示():
      
    global tow_to_five_list
    global d_okw_class_list
    global dy_label
    global key_word_label
    global d_okw_class_list
    global tow_to_five_label
    global first_to_five_label
    global first_to_five_list
    global key_word_list_content
    global ot_label
    global o_label_exit_flag
    global k_symbol_flag
    
    global model_label
    global model_kw

    global model_kw_label_flag
    global model_kw_list
    global model_kw_label
    global ignore_kw_label
    global o_kw_label_flag
    global dy_kw_model_dict
    
    global unidentified_word
    global unidentified_flag
    global unidentified_loc

    global smodel_kw_sum
    global smodel_kw_list
    global smodel_kw_label
    
    global model_kw

    global key_word_list
    global first_kw_flag
    global info_word_loc_list
    global fill_kw_loc
    global d_class_list
    global ref_sub_flag
    global p_e_flag
    global s_p_exist_flag
    global conversion_person
    global conversion_usr_info
    global storage_usr_info
    global preset_why
    global compen_label_flag
    global tow_to_five_exit_flag
    global model_exit_flag
    global smodel_exit_flag
    global k_symbol_flag
    
    fill_kw_loc_list = []
    fill_min_loc = 0
    fill_max_loc = 0
    
    fill_wd_add_list   = ''
    before_wd_add_list = ''
    after_wd_add_list  = ''
    
    fill_wd_list = []
    before_wd_list = []
    after_wd_list = []
    before_kw_len = 0
    after_kw_len = 0
    kw_list_all_len = len(info_word_loc_list) - 1

    methods = []
    attribute = []
    obj = []
    ref_dir_list = ['禁止','结果','后果','需要','方法','原因','条件','危害']
    preset = '禁止'
    #p_link_wd = '无法'

    seer_array = ''
    seer_list = []
    r_list_content = []
    match_key_list = []
    
    ref_sub_kw = ''
    dir_list = '大纲'
    t_obj = ''
    t_obj_len = 0
    t_obj_loc = 0
    answer_obj = ''
    answer_obj_len = 0
    answer_obj_loc = 0
    fill_flag = False
    t_obj_list = ''
    r_obj = ''
    c_obj = '对象'
    t_r_value = []
    default_obj = []
    answer_list = []
    r_value_flag = False
    obj_sub_flag = False
    get_answer_flag = False
    compound_dict = {}
    
#---------------------------------------------------------------------------------------------------    
    print('☀☀☀☀模型分析 --->>>>>> 条件_警示',model_kw)
    fill_flag = False

    fill_min_loc = min(fill_kw_loc)
    fill_max_loc = max(fill_kw_loc) - 1
    
    print('复查',model_kw_list,info_word_loc_list)
    print('填充前范围计算',fill_kw_loc,fill_min_loc,fill_max_loc)

#---------------------------------------------------------------------------------------------------
    #确定对象
    if p_e_flag:
       t_obj = conversion_person  
       print('✪✪✪✪确定对象',t_obj)
       
    elif first_kw_flag:
         for kwc,kwk in enumerate(key_word_list):
               
             #print('看看看',kwk)  
             r_list_content = getattr(eval(kwk),c_obj)()
             if r_list_content:
             #print('看看看',r_list_content)    
                t_obj = r_list_content[0]
                print('❤❤❤❤确定对象',t_obj,key_word_list)
                
             else:
                 print('××××找不到对象',t_obj,key_word_list)
                 
    elif tow_to_five_list:
         for ttc,ttk in enumerate(tow_to_five_list):
             r_value_flag = hasattr(eval(ttk),c_obj)
             if r_value_flag:
                t_r_value = getattr(eval(ttk)(),c_obj)()
                t_obj = t_r_value[0]
                print('♔♔♔♔确定对象:',t_obj)
#---------------------------------------------------------------------------------------------------
    if tow_to_five_label and ref_sub_flag == False:

         for tc,tk in enumerate(tow_to_five_label):
             #print('看这里',tk)  
             r_value_flag = hasattr(eval(t_obj),tk)#检测对象是否存在对应子项
             if r_value_flag:
                ref_sub_kw = tk#此处限定其它关键字总数为一个
                ref_dir_list.append(ref_sub_kw)
                ref_sub_flag = True
         print('▓▓▓▓检测',ref_sub_kw)
         

    if smodel_kw_label and ref_sub_flag == False:

         for sc,sk in enumerate(smodel_kw_label):
             #print('看这里',sk)  
             r_value_flag = hasattr(eval(t_obj),sk)#检测对象是否存在对应子项
             if r_value_flag:
                ref_sub_kw = sk#此处限定其它关键字总数为一个
                ref_dir_list.append(ref_sub_kw)
                ref_sub_flag = True 

         print('♦♦♦♦检测',ref_sub_kw)
     

    if key_word_label and ref_sub_flag == False:

       for kc,kk in enumerate(smodel_kw_label):
             #print('看这里',kk)  
             r_value_flag = hasattr(eval(t_obj),kk)#检测对象是否存在对应子项
             if r_value_flag:
                ref_sub_kw = kk#此处限定其它关键字总数为一个
                ref_dir_list.append(ref_sub_kw)
                ref_sub_flag = True    
    
       print('〓〓〓〓检测',ref_sub_kw)
    
         
    if ref_sub_flag == False:
       ref_sub_kw = preset   
       print('☎☎☎☎没有对应子项填入默认项',ref_sub_kw)
#---------------------------------------------------------------------------------------------------
    while fill_min_loc < fill_max_loc:
          fill_min_loc += 1
          fill_wd_list.append(info_word_loc_list[fill_min_loc])
          fill_wd_add_list = fill_wd_add_list + info_word_loc_list[fill_min_loc]
          print('开始填充并连接',fill_wd_list,fill_wd_add_list)

    answer_list.append(fill_wd_add_list)      
    print('查看插入填充子项信息',dy_kw_model_dict)
    
                    
#------------------------------------------------------------------------------------------------
    fill_min_loc = min(fill_kw_loc)
    #fill_max_loc = max(fill_kw_loc) - 1

    if fill_min_loc > 0:
          
       while before_kw_len < fill_min_loc:
             
             before_wd_list.append(info_word_loc_list[before_kw_len])
             before_wd_add_list += info_word_loc_list[before_kw_len]
             print('开始查询前移字符并连接',before_wd_list,before_wd_add_list)
             before_kw_len += 1
             

    print('查看前移子项填充信息',dy_kw_model_dict)
          
          
    #print('查看插入填充子项信息',dy_kw_model_dict) 
#---------------------------------------------------------------------------------------------------

    fill_flag = False
    fill_max_loc = max(fill_kw_loc)
    
    if fill_max_loc < kw_list_all_len:
          
       while fill_max_loc < kw_list_all_len:
             fill_max_loc += 1
             after_wd_list.append(info_word_loc_list[fill_max_loc])
             after_wd_add_list += info_word_loc_list[fill_max_loc]
             print('开始查询后移字符并连接',after_wd_list,after_wd_add_list)
             
    #after_wd_add_list = model_kw[0] + after_wd_add_list #链接模型关键字
    print('查看后移信息',after_wd_add_list) 
#----------------------------------------------------------------------------------------------------    
#----------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#合成新子项填充信息---------------------------------------------------------------------------------------------------

    if k_symbol_flag:
       if ref_sub_flag == False:   
          r_value_flag = hasattr(eval(t_obj),ref_sub_kw)
          if r_value_flag:
             print('✔✔✔✔对象存在对应子项:',ref_sub_kw)    
             seer_array =  getattr(eval(t_obj)(),ref_sub_kw)(fill_wd_add_list)
             if seer_array != False:
                   seer_array = t_obj + p_link_wd + seer_array
                   print('☁☁☁☁获取答案:',seer_array)
          else:
              print('✘✘✘✘对象没有对应子项:',ref_sub_kw)

       else:

          r_value_flag = hasattr(eval(t_obj),ref_sub_kw)
          if r_value_flag:
             print('✔✔✔✔对象存在对应子项:',ref_sub_kw)    
             seer_array =  getattr(eval(t_obj)(),ref_sub_kw)(fill_wd_add_list)
             if seer_array != False:
                   seer_array = t_obj + p_link_wd + seer_array
                   print('☁☁☁☁获取答案:',seer_array)
          else:
              print('✘✘✘✘对象没有对应子项:',ref_sub_kw)

              
              for rcc,rkk in enumerate(obj):
                  r_value_flag = hasattr(eval(t_obj),rkk)
                  if r_value_flag:
                     print('☛☛☛☛对象存在对应子项:',rkk)    
                     seer_array =  getattr(eval(t_obj)(),rkk)(fill_wd_add_list)
                     print('看看看',seer_array)
                     if seer_array != False:
                        seer_array = t_obj + p_link_wd + seer_array   
                        print('♨♨♨♨获取答案:',seer_array,rkk)
                        break
                  else:
                      print('✘✘✘✘对象没有对应子项:',rkk)  

#获取答案失败,更改参考值----------------------------------------------------------------------------
       if get_answer_flag == True:
          print('☂☂☂☂☂获取答案失败,更改参考值:')
          r_value_flag = hasattr(eval(t_obj),ref_sub_kw)
          if r_value_flag:
             print('✔✔✔✔对象存在对应子项:',ref_sub_kw)    
             seer_array =  getattr(eval(t_obj)(),ref_sub_kw)(before_wd_add_list)
             if seer_array != False:
                   #seer_array = t_obj + seer_array
                   get_answer_flag = True
                   print('☁☁☁☁获取答案:',seer_array)
          else:
              print('✘✘✘✘对象没有对应子项:',ref_sub_kw)

       else:

          r_value_flag = hasattr(eval(t_obj),ref_sub_kw)
          if r_value_flag:
             print('✔✔✔✔对象存在对应子项:',ref_sub_kw)    
             seer_array =  getattr(eval(t_obj)(),ref_sub_kw)(before_wd_add_list)
             if seer_array != False:
                   #seer_array = t_obj + seer_array
                   get_answer_flag = True
                   print('☁☁☁☁获取答案:',seer_array)
          else:
              print('✘✘✘✘对象没有对应子项:',ref_sub_kw)

              
              for rcc,rkk in enumerate(obj):
                  r_value_flag = hasattr(eval(t_obj),rkk)
                  if r_value_flag:
                     print('☛☛☛☛对象存在对应子项:',rkk)    
                     #seer_array =  getattr(eval(t_obj)(),rkk)(after_wd_add_list)
                     print('看看看',seer_array)
                     if seer_array != False:
                        seer_array = t_obj + seer_array
                        get_answer_flag = True
                        print('♨♨♨♨获取答案:',seer_array,rkk)
                        break
                  else:
                      print('✘✘✘✘对象没有对应子项:',rkk)
                      
#---------------------------------------------------------------------------------------------------
       
    else:
        print('☯☯☯☯检测',answer_list)   
        compound_dict = dict.fromkeys(answer_list,after_wd_add_list)#注意
        print('➹➹➹➹准备填入对象对应子项信息',compound_dict)
#查询对象并填充信息------------------------------------------------------------------------------------------------------        
       
        for rcc ,rkk in enumerate(ref_dir_list):      
            r_value_flag = hasattr(eval(t_obj),rkk)
    
            if r_value_flag:
               print('◑◑◑◑存在对应子项准备填入信息',t_obj,rkk)
               getattr(eval(t_obj)(),rkk)(compound_dict)
#---------------------------------------------------------------------------------------------------
def 条件_后果():
      
    global tow_to_five_list
    global d_okw_class_list
    global dy_label
    global key_word_label
    global d_okw_class_list
    global tow_to_five_label
    global first_to_five_label
    global first_to_five_list
    global key_word_list_content
    global ot_label
    global o_label_exit_flag
    global k_symbol_flag
    
    global model_label
    global model_kw

    global model_kw_label_flag
    global model_kw_list
    global model_kw_label
    global ignore_kw_label
    global o_kw_label_flag
    global dy_kw_model_dict
    
    global unidentified_word
    global unidentified_flag
    global unidentified_loc

    global smodel_kw_sum
    global smodel_kw_list
    global smodel_kw_label
    
    global model_kw

    global key_word_list
    global first_kw_flag
    global info_word_loc_list
    global fill_kw_loc
    global d_class_list
    global ref_sub_flag
    global p_e_flag
    global s_p_exist_flag
    global conversion_person
    global conversion_usr_info
    global storage_usr_info
    global preset_why
    global compen_label_flag
    global tow_to_five_exit_flag
    global model_exit_flag
    global smodel_exit_flag
    global k_symbol_flag
    
    fill_kw_loc_list = []
    fill_min_loc = 0
    fill_max_loc = 0
    
    fill_wd_add_list   = ''
    before_wd_add_list = ''
    after_wd_add_list  = ''
    
    fill_wd_list = []
    before_wd_list = []
    after_wd_list = []
    before_kw_len = 0
    after_kw_len = 0
    kw_list_all_len = len(info_word_loc_list) - 1

    methods = []
    attribute = []
    obj = ['后果','结果','方法','需要','原因','条件']
    ref_dir_list = []
    preset = '后果'
    p_link_wd = '无法'

    seer_array = ''
    seer_list = []
    r_list_content = []
    match_key_list = []
    
    ref_sub_kw = ''
    dir_list = '大纲'
    t_obj = ''
    t_obj_len = 0
    t_obj_loc = 0
    answer_obj = ''
    answer_obj_len = 0
    answer_obj_loc = 0
    fill_flag = False
    t_obj_list = ''
    r_obj = ''
    c_obj = '对象'
    t_r_value = []
    default_obj = []
    answer_list = []
    r_value_flag = False
    obj_sub_flag = False
    get_answer_flag = False
    compound_dict = {}
    
#---------------------------------------------------------------------------------------------------    
    print('☀☀☀☀模型分析 --->>>>>> 条件_后果',model_kw)
    fill_flag = False

    fill_min_loc = min(fill_kw_loc)
    fill_max_loc = max(fill_kw_loc) - 1
    
    print('复查',model_kw_list,info_word_loc_list)
    print('填充前范围计算',fill_kw_loc,fill_min_loc,fill_max_loc)

#---------------------------------------------------------------------------------------------------
    #确定对象
    if p_e_flag:
       t_obj = conversion_person  
       print('✪✪✪✪确定对象',t_obj)
       
    elif first_kw_flag:
         for kwc,kwk in enumerate(key_word_list):
               
             #print('看看看',kwk)  
             r_list_content = getattr(eval(kwk),c_obj)()
             if r_list_content:
             #print('看看看',r_list_content)    
                t_obj = r_list_content[0]
                print('❤❤❤❤确定对象',t_obj,key_word_list)
                
             else:
                 print('××××找不到对象',t_obj,key_word_list)
                 
    elif tow_to_five_list:
         for ttc,ttk in enumerate(tow_to_five_list):
             r_value_flag = hasattr(eval(ttk),c_obj)
             if r_value_flag:
                t_r_value = getattr(eval(ttk)(),c_obj)()
                t_obj = t_r_value[0]
                print('♔♔♔♔确定对象:',t_obj)
#---------------------------------------------------------------------------------------------------
    if tow_to_five_label and ref_sub_flag == False:

         for tc,tk in enumerate(tow_to_five_label):
             #print('看这里',tk)  
             r_value_flag = hasattr(eval(t_obj),tk)#检测对象是否存在对应子项
             if r_value_flag:
                ref_sub_kw = tk#此处限定其它关键字总数为一个
                ref_dir_list.append(ref_sub_kw)
                ref_sub_flag = True
         print('▓▓▓▓检测',ref_sub_kw)
         

    if smodel_kw_label and ref_sub_flag == False:

         for sc,sk in enumerate(smodel_kw_label):
             print('看这里',sk)  
             r_value_flag = hasattr(eval(t_obj),sk)#检测对象是否存在对应子项
             if r_value_flag:
                ref_sub_kw = sk#此处限定其它关键字总数为一个
                ref_dir_list.append(ref_sub_kw)
                ref_sub_flag = True 

         print('♦♦♦♦检测',ref_sub_kw)
     

    if key_word_label and ref_sub_flag == False:

       for kc,kk in enumerate(smodel_kw_label):
             #print('看这里',kk)  
             r_value_flag = hasattr(eval(t_obj),kk)#检测对象是否存在对应子项
             if r_value_flag:
                ref_sub_kw = kk#此处限定其它关键字总数为一个
                ref_dir_list.append(ref_sub_kw)
                ref_sub_flag = True    
    
       print('〓〓〓〓检测',ref_sub_kw)
    
         
    if ref_sub_flag == False:
       ref_sub_kw = preset   
       print('☎☎☎☎没有对应子项填入默认项',preset)
#---------------------------------------------------------------------------------------------------
    if fill_min_loc > 0:
          
       while before_kw_len < fill_min_loc:
             before_kw_len += 1
             before_wd_list.append(info_word_loc_list[before_kw_len])
             before_wd_add_list += info_word_loc_list[before_kw_len]             
             
             print('开始查询前移字符并连接',before_wd_list,before_wd_add_list)
                          
    #before_wd_add_list += model_kw[0] #链接模型关键字        
    answer_list.append(before_wd_add_list)
#---------------------------------------------------------------------------------------------------
    while fill_min_loc < fill_max_loc:
          fill_min_loc += 1
          fill_wd_list.append(info_word_loc_list[fill_min_loc])
          fill_wd_add_list = fill_wd_add_list + info_word_loc_list[fill_min_loc]
          print('开始填充并连接',fill_wd_list,fill_wd_add_list)
          
          
    #print('查看插入填充子项信息',dy_kw_model_dict) 
#---------------------------------------------------------------------------------------------------
    fill_flag = False
    fill_max_loc = max(fill_kw_loc)
    
    if fill_max_loc < kw_list_all_len:
          
       while fill_max_loc < kw_list_all_len:
             fill_max_loc += 1
             after_wd_list.append(info_word_loc_list[fill_max_loc])
             after_wd_add_list += info_word_loc_list[fill_max_loc]
             print('开始查询后移字符并连接',after_wd_list,after_wd_add_list)
             
    after_wd_add_list = model_kw[0] + after_wd_add_list #链接模型关键字
    print('查看后移信息',after_wd_add_list) 
#----------------------------------------------------------------------------------------------------    
#----------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#合成新子项填充信息---------------------------------------------------------------------------------------------------

    if k_symbol_flag:
       if ref_sub_flag == False:
             
          r_value_flag = hasattr(eval(t_obj),ref_sub_kw)
          if r_value_flag:
             print('✔✔✔✔对象存在对应子项:',ref_sub_kw)    
             seer_array =  getattr(eval(t_obj)(),ref_sub_kw)(fill_wd_add_list)
             
             if seer_array != False:
                    
                   seer_array = t_obj + p_link_wd + seer_array
                   print('☁☁☁☁获取答案:',seer_array)
          else:
              print('✘✘✘✘对象没有对应子项:',ref_sub_kw)

       else:

          r_value_flag = hasattr(eval(t_obj),ref_sub_kw)
          if r_value_flag:
             print('✔✔✔✔对象存在对应子项:',ref_sub_kw)    
             seer_array =  getattr(eval(t_obj)(),ref_sub_kw)(fill_wd_add_list)
             if seer_array != False:
                   seer_array = t_obj + p_link_wd + seer_array
                   print('❁❁❁❁获取答案:',seer_array)
          else:
              print('✘✘✘✘对象没有对应子项:',ref_sub_kw)

              
              for rcc,rkk in enumerate(obj):
                  r_value_flag = hasattr(eval(t_obj),rkk)
                  if r_value_flag:
                     print('✈✈✈✈对象存在对应子项:',rkk)    
                     seer_array =  getattr(eval(t_obj)(),rkk)(fill_wd_add_list)
                     print('看看看',seer_array)
                     if seer_array != False:
                        seer_array = t_obj + p_link_wd + seer_array   
                        print('♨♨♨♨获取答案:',seer_array,rkk)
                        break
                  else:
                      print('✘✘✘✘对象没有对应子项:',rkk)  

#获取答案失败,更改参考值----------------------------------------------------------------------------
       if get_answer_flag == False:
          if ref_sub_flag == False:   
             print('☂☂☂☂☂获取答案失败,更改参考值:')
             r_value_flag = hasattr(eval(t_obj),ref_sub_kw)
             if r_value_flag:
                print('✔✔✔✔对象存在对应子项:',ref_sub_kw)    
                seer_array =  getattr(eval(t_obj)(),ref_sub_kw)(before_wd_add_list)
                if seer_array != False:
                   #seer_array = t_obj + seer_array
                   get_answer_flag = True
                   print('☁☁☁☁获取答案:',seer_array)
             else:
                 print('✘✘✘✘对象没有对应子项:',ref_sub_kw)

          else:

              r_value_flag = hasattr(eval(t_obj),ref_sub_kw)
              if r_value_flag:
                 print('✔✔✔✔对象存在对应子项:',ref_sub_kw)    
                 seer_array =  getattr(eval(t_obj)(),ref_sub_kw)(before_wd_add_list)
                 if seer_array != False:
                   #seer_array = t_obj + seer_array
                    get_answer_flag = True
                    print('❁❁❁❁获取答案:',seer_array)
              else:
                  print('✘✘✘✘对象没有对应子项:',ref_sub_kw)

              
                  for rcc,rkk in enumerate(obj):
                      r_value_flag = hasattr(eval(t_obj),rkk)
                      if r_value_flag:
                         print('☛☛☛☛对象存在对应子项:',rkk)    
                     #seer_array =  getattr(eval(t_obj)(),rkk)(after_wd_add_list)
                         print('看看看',seer_array)
                         if seer_array != False:
                            seer_array = t_obj + seer_array
                            get_answer_flag = True
                            print('♨♨♨♨获取答案:',seer_array,rkk)
                            break
                      else:
                          print('✘✘✘✘对象没有对应子项:',rkk)
                      
#---------------------------------------------------------------------------------------------------
       if get_answer_flag == False:
          print('☈☈☈☈获取答案再次失败,进入应急状态:')
          for rcc,rkk in enumerate(obj):
                  r_value_flag = hasattr(eval(t_obj),rkk)
                  if r_value_flag:
                     print('♛♛♛♛对象存在对应子项:',rkk)    
                     seer_array =  getattr(eval(t_obj)(),rkk)(fill_wd_add_list)
                     print('看看看',seer_array)
                     if seer_array != False:
                        seer_array = t_obj +  seer_array   
                        print('ிிிி获取答案:',seer_array,rkk)
                        break
                  else:
                      print('✍✍✍✍对象没有对应子项:',rkk) 

#---------------------------------------------------------------------------------------------------       
    else:
        print('☯☯☯☯检测',answer_list)   
        compound_dict = dict.fromkeys(answer_list,after_wd_add_list)#注意
        print('准备填入对象对应子项信息',compound_dict)
#查询对象并填充信息------------------------------------------------------------------------------------------------------        
       
        for rcc ,rkk in enumerate(ref_dir_list):      
            r_value_flag = hasattr(eval(t_obj),rkk)
    
            if r_value_flag:
       
               getattr(eval(t_obj)(),rkk)(compound_dict)

#///////////////////////////////////////////////////////////////////////////////////////////////////
def 获得_条件():
      
    global tow_to_five_list
    global d_okw_class_list
    global dy_label
    global key_word_label
    global d_okw_class_list
    global tow_to_five_label
    global first_to_five_label
    global first_to_five_list
    global key_word_list_content
    global ot_label
    global o_label_exit_flag
    global k_symbol_flag
    
    global model_label
    global model_kw

    global model_kw_label_flag
    global model_kw_list
    global model_kw_label
    global ignore_kw_label
    global o_kw_label_flag
    global dy_kw_model_dict
    
    global unidentified_word
    global unidentified_flag
    global unidentified_loc

    global smodel_kw_sum
    global smodel_kw_list
    global smodel_kw_label
    
    global model_kw

    global key_word_list
    global first_kw_flag
    global info_word_loc_list
    global fill_kw_loc
    global d_class_list
    global ref_sub_flag
    global p_e_flag
    global s_p_exist_flag
    global conversion_person
    global conversion_usr_info
    global storage_usr_info
    global preset_why
    global compen_label_flag
    global tow_to_five_exit_flag
    global model_exit_flag
    global smodel_exit_flag
    global k_symbol_flag
    global force_out_ansewr
    
    fill_kw_loc_list = []
    fill_min_loc = 0
    fill_max_loc = 0
    
    fill_wd_add_list   = ''
    before_wd_add_list = ''
    after_wd_add_list  = ''
    
    fill_wd_list = []
    before_wd_list = []
    after_wd_list = []
    before_kw_len = 0
    after_kw_len = 0
    kw_list_all_len = len(info_word_loc_list) - 1

    methods = []
    attribute = []
    obj = ['禁止','结果','后果','需要','方法','原因','条件','危害']
    ref_dir_list = []
    preset = '需要'
    p_link_wd = '不'
    count_kw = '和'

    seer_array = ''
    count_array = ''
    seer_list = []
    r_list_content = []
    match_key_list = []
    
    ref_sub_kw = ''
    dir_list = '大纲'
    t_obj = ''
    t_obj_len = 0
    t_obj_loc = 0
    answer_obj = ''
    answer_obj_len = 0
    answer_obj_loc = 0
    fill_flag = False
    t_obj_list = ''
    r_obj = ''
    c_obj = '对象'
    t_r_value = []
    default_obj = []
    answer_list = []
    r_value_flag = False
    obj_sub_flag = False
    get_answer_flag = False
    compound_dict = {}
    
#---------------------------------------------------------------------------------------------------    
    print('☀☀☀☀模型分析 --->>>>>> 获得_条件',model_kw)
    fill_flag = False
    fill_max_loc = max(fill_kw_loc)
    fill_min_loc = min(fill_kw_loc)

#---------------------------------------------------------------------------------------------------
    #确定对象 
    if p_e_flag:
       t_obj = conversion_person  
       print('✪✪✪✪确定对象',t_obj)
       
    elif first_kw_flag:
         for kwc,kwk in enumerate(key_word_list):
               
             #print('看看看',kwk)  
             r_list_content = getattr(eval(kwk),c_obj)()
             if r_list_content:
             #print('看看看',r_list_content)    
                t_obj = r_list_content[0]
                print('❤❤❤❤确定对象',t_obj,key_word_list)
                
             else:
                 print('××××找不到对象',t_obj,key_word_list)
                 
    elif tow_to_five_list:
         for ttc,ttk in enumerate(tow_to_five_list):
             r_value_flag = hasattr(eval(ttk),c_obj)
             if r_value_flag:
                t_r_value = getattr(eval(ttk)(),c_obj)()
                t_obj = t_r_value[0]
                print('♔♔♔♔确定对象:',t_obj)
#---------------------------------------------------------------------------------------------------
    if tow_to_five_label and ref_sub_flag == False:

         for tc,tk in enumerate(tow_to_five_label):
             #print('看这里',tk)  
             r_value_flag = hasattr(eval(t_obj),tk)#检测对象是否存在对应子项
             if r_value_flag:
                ref_sub_kw = tk#此处限定其它关键字总数为一个
                ref_dir_list.append(ref_sub_kw)
                ref_sub_flag = True
         print('▓▓▓▓检测',ref_sub_kw)
         

    if smodel_kw_label and ref_sub_flag == False:

         for sc,sk in enumerate(smodel_kw_label):
             #print('看这里',sk)  
             r_value_flag = hasattr(eval(t_obj),sk)#检测对象是否存在对应子项
             if r_value_flag:
                ref_sub_kw = sk#此处限定其它关键字总数为一个
                ref_dir_list.append(ref_sub_kw)
                ref_sub_flag = True 

         print('♦♦♦♦检测',ref_sub_kw)
     

    if key_word_label and ref_sub_flag == False:

       for kc,kk in enumerate(smodel_kw_label):
             #print('看这里',kk)  
             r_value_flag = hasattr(eval(t_obj),kk)#检测对象是否存在对应子项
             if r_value_flag:
                ref_sub_kw = kk#此处限定其它关键字总数为一个
                ref_dir_list.append(ref_sub_kw)
                ref_sub_flag = True    
    
       print('〓〓〓〓检测',ref_sub_kw)
    
         
    if ref_sub_flag == False:
       ref_sub_kw = preset   
       print('☎☎☎☎没有对应子项填入默认项',ref_sub_kw)
#---------------------------------------------------------------------------------------------------
    if fill_min_loc > 0:
          
       while before_kw_len < fill_min_loc:
             before_kw_len += 1
             before_wd_list.append(info_word_loc_list[before_kw_len])
             before_wd_add_list += info_word_loc_list[before_kw_len]             
             
             print('开始查询前移字符并连接',before_wd_list,before_wd_add_list)
                          
    #before_wd_add_list += model_kw[0] #链接模型关键字        
    answer_list.append(before_wd_add_list)
#---------------------------------------------------------------------------------------------------
    while fill_min_loc < fill_max_loc:
          fill_min_loc += 1
          fill_wd_list.append(info_word_loc_list[fill_min_loc])
          fill_wd_add_list = fill_wd_add_list + info_word_loc_list[fill_min_loc]
          print('开始填充并连接',fill_wd_list,fill_wd_add_list)
          
          
    #print('查看插入填充子项信息',dy_kw_model_dict) 
#---------------------------------------------------------------------------------------------------
    fill_flag = False
    fill_max_loc = max(fill_kw_loc)
    
    if fill_max_loc < kw_list_all_len:
          
       while fill_max_loc < kw_list_all_len:
             fill_max_loc += 1
             after_wd_list.append(info_word_loc_list[fill_max_loc])
             after_wd_add_list += info_word_loc_list[fill_max_loc]
             print('开始查询后移字符并连接',after_wd_list,after_wd_add_list)
             
    after_wd_add_list = model_kw[0] + after_wd_add_list #链接模型关键字
    print('查看后移信息',after_wd_add_list) 
#----------------------------------------------------------------------------------------------------    
#----------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#合成新子项填充信息---------------------------------------------------------------------------------------------------

    if k_symbol_flag:
       if ref_sub_flag == False:   
          r_value_flag = hasattr(eval(t_obj),ref_sub_kw)
          if r_value_flag:
             print('✔✔✔✔对象存在对应子项:',ref_sub_kw)    
             seer_array =  getattr(eval(t_obj)(),ref_sub_kw)(after_wd_add_list)
             if seer_array != False:
                   #seer_array = t_obj + seer_array
                   get_answer_flag = True
                   print('☁☁☁☁获取答案:',seer_array)
          else:
              print('✘✘✘✘对象没有对应子项:',ref_sub_kw)

       else:

          r_value_flag = hasattr(eval(t_obj),ref_sub_kw)
          if r_value_flag:
             print('✔✔✔✔对象存在对应子项:',ref_sub_kw)    
             seer_array =  getattr(eval(t_obj)(),ref_sub_kw)(after_wd_add_list)
             if seer_array != False:
                   #seer_array = t_obj + seer_array
                   get_answer_flag = True
                   print('☁☁☁☁获取答案:',seer_array)
          else:
              print('✘✘✘✘对象没有对应子项:',ref_sub_kw)

              
              for rcc,rkk in enumerate(obj):
                  r_value_flag = hasattr(eval(t_obj),rkk)
                  if r_value_flag:
                     print('☛☛☛☛对象存在对应子项:',rkk)    
                     #seer_array =  getattr(eval(t_obj)(),rkk)(after_wd_add_list)
                     print('看看看',seer_array)
                     if seer_array != False:
                        seer_array = t_obj + seer_array
                        get_answer_flag = True
                        print('♨♨♨♨获取答案:',seer_array,rkk)
                        break
                  else:
                      print('✘✘✘✘对象没有对应子项:',rkk)

#获取答案失败,更改参考值----------------------------------------------------------------------------
       if get_answer_flag == False:
          print('☂☂☂☂☂获取答案失败,更改参考值:')
          r_value_flag = hasattr(eval(t_obj),ref_sub_kw)
          if r_value_flag:
             print('✔✔✔✔对象存在对应子项:',ref_sub_kw)    
             seer_array =  getattr(eval(t_obj)(),ref_sub_kw)(before_wd_add_list)
             if seer_array != False:
                   #seer_array = t_obj + seer_array
                   get_answer_flag = True
                   print('☁☁☁☁获取答案:',seer_array)
          else:
              print('✘✘✘✘对象没有对应子项:',ref_sub_kw)

       else:

          r_value_flag = hasattr(eval(t_obj),ref_sub_kw)
          if r_value_flag:
             print('✔✔✔✔对象存在对应子项:',ref_sub_kw)    
             seer_array =  getattr(eval(t_obj)(),ref_sub_kw)(before_wd_add_list)
             if seer_array != False:
                   #seer_array = t_obj + seer_array
                   get_answer_flag = True
                   print('☁☁☁☁获取答案:',seer_array)
          else:
              print('✘✘✘✘对象没有对应子项:',ref_sub_kw)

              
              for rcc,rkk in enumerate(obj):
                  r_value_flag = hasattr(eval(t_obj),rkk)
                  if r_value_flag:
                     print('☛☛☛☛对象存在对应子项:',rkk)    
                     #seer_array =  getattr(eval(t_obj)(),rkk)(after_wd_add_list)
                     print('看看看',seer_array)
                     if seer_array != False:
                        seer_array = t_obj + seer_array
                        get_answer_flag = True
                        print('♨♨♨♨获取答案:',seer_array,rkk)
                        break
                  else:
                      print('✘✘✘✘对象没有对应子项:',rkk)
#---------------------------------------------------------------------------------------------------
       if get_answer_flag == False:
          print('☈☈☈☈获取答案再次失败,进入应急状态:')             
          force_out_ansewr = True
          
          r_value_flag = hasattr(eval(t_obj),ref_sub_kw)
          if r_value_flag:
             print('✔✔✔✔对象存在对应子项:',ref_sub_kw)    
             seer_array =  getattr(eval(t_obj)(),ref_sub_kw)(before_wd_add_list)#此时的参数已无意义
             print('查询',seer_array)
             if seer_array != False:
                   #seer_array = t_obj + seer_array 
                   get_answer_flag = True
                   
#以下代码将返回字典作为答案，提取字典键输出答案---------------------------------------------------------------------------------------------------
                   
                       
                   for sac,sak in enumerate(seer_array):
                       for src,srk in sak.items():
                           for rcc,rkk in enumerate(remove_wd_list):#检测是否存在需排除的字符
                               if rkk in src:
                                  print('找到',rkk)   
                                  r_obj = src   
                                  t_obj_len = len(rkk)
                                  t_obj_loc = r_obj.find(rkk)
                                  r_obj = r_obj[0:t_obj_loc] + r_obj[t_obj_loc + t_obj_len:]
                                  src = r_obj
                                  break
                           default_obj.append(src)

                   if len(default_obj) > 1:
                      for acc,akk in enumerate(default_obj):
                          print('检测',acc,akk)  
                          count_array = akk + count_kw  
                          count_array = t_obj + preset + count_array
                      print('☁☁☁☁获取答案:',count_array)
                      
                   elif len(default_obj) == 1:
                       count_array = default_obj[0]
                       count_array = t_obj + preset + count_array
                       print('✿✿✿✿获取答案:',count_array)
          else:
              print('✘✘✘✘对象没有对应子项:',ref_sub_kw)
#----------------------------------------------------------------------------------------------------
              
              for rcc,rkk in enumerate(obj):
                  r_value_flag = hasattr(eval(t_obj),rkk)
                  if r_value_flag:
                     print('☛☛☛☛对象存在对应子项:',rkk)    
                     seer_array =  getattr(eval(t_obj)(),rkk)(after_wd_add_list)
                     #print('看看看',seer_array)
                     if seer_array != False:
                        #seer_array = t_obj + seer_array
                        get_answer_flag = True
#----------------------------------------------------------------------------------------------------
                     for sac,sak in enumerate(seer_array):
                       for src,srk in sak.items():
                           default_obj.append(src)
 
                     if len(default_obj) > 1:
                        for acc,akk in enumerate(default_obj):
                            print('查询',acc,akk)  
                            count_array = akk + count_kw  
                          
                            print('♨♨♨♨获取答案:',count_array)
                            break
                        
                     elif len(default_obj) == 1:
                           count_array = default_obj[0]
                           print('♨♨♨♨获取答案:',count_array)
 
                           break
                  else:
                      print('✘✘✘✘对象没有对应子项:',rkk)
          
#---------------------------------------------------------------------------------------------------       
                   
#---------------------------------------------------------------------------------------------------

    else:
        print('☯☯☯☯检测',answer_list)   
        compound_dict = dict.fromkeys(answer_list,after_wd_add_list)#注意
        print('◐◐◐◐准备填入对象对应子项信息',compound_dict)
#查询对象并填充信息------------------------------------------------------------------------------------------------------        
       
        for rcc ,rkk in enumerate(ref_dir_list):      
            r_value_flag = hasattr(eval(t_obj),rkk)
    
            if r_value_flag:
       
               getattr(eval(t_obj)(),rkk)(compound_dict)               

#///////////////////////////////////////////////////////////////////////////////////////////////////
def 获得_结果():
      
    global tow_to_five_list
    global d_okw_class_list
    global dy_label
    global key_word_label
    global d_okw_class_list
    global tow_to_five_label
    global first_to_five_label
    global first_to_five_list
    global key_word_list_content
    global ot_label
    global o_label_exit_flag
    global k_symbol_flag
    
    global model_label
    global model_kw

    global model_kw_label_flag
    global model_kw_list
    global model_kw_label
    global ignore_kw_label
    global o_kw_label_flag
    global dy_kw_model_dict
    
    global unidentified_word
    global unidentified_flag
    global unidentified_loc

    global smodel_kw_sum
    global smodel_kw_list
    global smodel_kw_label
    
    global model_kw

    global key_word_list
    global first_kw_flag
    global info_word_loc_list
    global fill_kw_loc
    global d_class_list
    global ref_sub_flag
    global p_e_flag
    global s_p_exist_flag
    global conversion_person
    global conversion_usr_info
    global storage_usr_info
    global preset_why
    global compen_label_flag
    global tow_to_five_exit_flag
    global model_exit_flag
    global smodel_exit_flag
    global k_symbol_flag
    
    fill_kw_loc_list = []
    fill_min_loc = 0
    fill_max_loc = 0
    
    fill_wd_add_list   = ''
    before_wd_add_list = ''
    after_wd_add_list  = ''
    
    fill_wd_list = []
    before_wd_list = []
    after_wd_list = []
    before_kw_len = 0
    after_kw_len = 0
    kw_list_all_len = len(info_word_loc_list) - 1

    methods = []
    attribute = []
    obj = ['方法','结果','内容','原因','条件']
    ref_dir_list = []
    preset = '后果'
    #p_link_wd = '无法'

    seer_array = ''
    seer_list = []
    r_list_content = []
    match_key_list = []
    
    ref_sub_kw = ''
    dir_list = '大纲'
    t_obj = ''
    t_obj_len = 0
    t_obj_loc = 0
    answer_obj = ''
    answer_obj_len = 0
    answer_obj_loc = 0
    fill_flag = False
    t_obj_list = ''
    r_obj = ''
    c_obj = '对象'
    t_r_value = []
    default_obj = []
    answer_list = []
    r_value_flag = False
    obj_sub_flag = False
    get_answer_flag = False
    compound_dict = {}
    
#---------------------------------------------------------------------------------------------------    
    print('☀☀☀☀模型分析 --->>>>>> 获得_结果',model_kw)
    fill_flag = False
    fill_max_loc = max(fill_kw_loc)
    fill_min_loc = min(fill_kw_loc)

#---------------------------------------------------------------------------------------------------
    #确定对象 
    if p_e_flag:
       t_obj = conversion_person  
       print('✪✪✪✪确定对象',t_obj)
       
    elif first_kw_flag:
         for kwc,kwk in enumerate(key_word_list):
               
             #print('看看看',kwk)  
             r_list_content = getattr(eval(kwk),c_obj)()
             if r_list_content:
             #print('看看看',r_list_content)    
                t_obj = r_list_content[0]
                print('❤❤❤❤确定对象',t_obj,key_word_list)
                
             else:
                 print('××××找不到对象',t_obj,key_word_list)
                 
    elif tow_to_five_list:
         for ttc,ttk in enumerate(tow_to_five_list):
             r_value_flag = hasattr(eval(ttk),c_obj)
             if r_value_flag:
                t_r_value = getattr(eval(ttk)(),c_obj)()
                t_obj = t_r_value[0]
                print('♔♔♔♔确定对象:',t_obj)
#---------------------------------------------------------------------------------------------------
    if tow_to_five_label and ref_sub_flag == False:

         for tc,tk in enumerate(tow_to_five_label):
             #print('看这里',tk)  
             r_value_flag = hasattr(eval(t_obj),tk)#检测对象是否存在对应子项
             if r_value_flag:
                ref_sub_kw = tk#此处限定其它关键字总数为一个
                ref_dir_list.append(ref_sub_kw)
                ref_sub_flag = True
         print('▓▓▓▓检测',ref_sub_kw)
         

    if smodel_kw_label and ref_sub_flag == False:

         for sc,sk in enumerate(smodel_kw_label):
             #print('看这里',sk)  
             r_value_flag = hasattr(eval(t_obj),sk)#检测对象是否存在对应子项
             if r_value_flag:
                ref_sub_kw = sk#此处限定其它关键字总数为一个
                ref_dir_list.append(ref_sub_kw)
                ref_sub_flag = True 

         print('♦♦♦♦检测',ref_sub_kw)
     

    if key_word_label and ref_sub_flag == False:

       for kc,kk in enumerate(smodel_kw_label):
             #print('看这里',kk)  
             r_value_flag = hasattr(eval(t_obj),kk)#检测对象是否存在对应子项
             if r_value_flag:
                ref_sub_kw = kk#此处限定其它关键字总数为一个
                ref_dir_list.append(ref_sub_kw)
                ref_sub_flag = True    
    
       print('〓〓〓〓检测',ref_sub_kw)
    
         
    if ref_sub_flag == False:
       ref_sub_kw = preset   
       print('☎☎☎☎没有对应子项填入默认项',ref_sub_kw)
#---------------------------------------------------------------------------------------------------
    if fill_min_loc > 0:
          
       while before_kw_len < fill_min_loc:
             before_kw_len += 1
             before_wd_list.append(info_word_loc_list[before_kw_len])
             before_wd_add_list += info_word_loc_list[before_kw_len]             
             
             print('开始查询前移字符并连接',before_wd_list,before_wd_add_list)
                          
    #before_wd_add_list += model_kw[0] #链接模型关键字        
    answer_list.append(before_wd_add_list)
#---------------------------------------------------------------------------------------------------
    while fill_min_loc < fill_max_loc:
          fill_min_loc += 1
          fill_wd_list.append(info_word_loc_list[fill_min_loc])
          fill_wd_add_list = fill_wd_add_list + info_word_loc_list[fill_min_loc]
          print('开始填充并连接',fill_wd_list,fill_wd_add_list)
          
          
    #print('查看插入填充子项信息',dy_kw_model_dict) 
#---------------------------------------------------------------------------------------------------
    fill_flag = False
    fill_max_loc = max(fill_kw_loc)
    
    if fill_max_loc < kw_list_all_len:
          
       while fill_max_loc < kw_list_all_len:
             fill_max_loc += 1
             after_wd_list.append(info_word_loc_list[fill_max_loc])
             after_wd_add_list += info_word_loc_list[fill_max_loc]
             print('开始查询后移字符并连接',after_wd_list,after_wd_add_list)
             
    after_wd_add_list = model_kw[0] + after_wd_add_list #链接模型关键字
    print('查看后移信息',after_wd_add_list) 
#----------------------------------------------------------------------------------------------------    
#----------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#合成新子项填充信息---------------------------------------------------------------------------------------------------

    if k_symbol_flag:
       if ref_sub_flag == False:   
          r_value_flag = hasattr(eval(t_obj),ref_sub_kw)
          if r_value_flag:
             print('✔✔✔✔对象存在对应子项:',ref_sub_kw)    
             seer_array =  getattr(eval(t_obj)(),ref_sub_kw)(after_wd_add_list)
             if seer_array != False:
                   #seer_array = t_obj + seer_array
                   get_answer_flag = True
                   print('☁☁☁☁获取答案:',seer_array)
          else:
              print('✘✘✘✘对象没有对应子项:',ref_sub_kw)

       else:

          r_value_flag = hasattr(eval(t_obj),ref_sub_kw)
          if r_value_flag:
             print('✔✔✔✔对象存在对应子项:',ref_sub_kw)    
             seer_array =  getattr(eval(t_obj)(),ref_sub_kw)(after_wd_add_list)
             if seer_array != False:
                   #seer_array = t_obj + seer_array
                   get_answer_flag = True
                   print('☁☁☁☁获取答案:',seer_array)
          else:
              print('✘✘✘✘对象没有对应子项:',ref_sub_kw)

              
              for rcc,rkk in enumerate(obj):
                  r_value_flag = hasattr(eval(t_obj),rkk)
                  if r_value_flag:
                     print('☛☛☛☛对象存在对应子项:',rkk)    
                     #seer_array =  getattr(eval(t_obj)(),rkk)(after_wd_add_list)
                     print('看看看',seer_array)
                     if seer_array != False:
                        seer_array = t_obj + seer_array
                        get_answer_flag = True
                        print('♨♨♨♨获取答案:',seer_array,rkk)
                        break
                  else:
                      print('✘✘✘✘对象没有对应子项:',rkk)

#获取答案失败,更改参考值----------------------------------------------------------------------------
       if get_answer_flag == True:
          print('☂☂☂☂☂获取答案失败,更改参考值:')
          r_value_flag = hasattr(eval(t_obj),ref_sub_kw)
          if r_value_flag:
             print('✔✔✔✔对象存在对应子项:',ref_sub_kw)    
             seer_array =  getattr(eval(t_obj)(),ref_sub_kw)(before_wd_add_list)
             if seer_array != False:
                   #seer_array = t_obj + seer_array
                   get_answer_flag = True
                   print('☁☁☁☁获取答案:',seer_array)
          else:
              print('✘✘✘✘对象没有对应子项:',ref_sub_kw)

       else:

          r_value_flag = hasattr(eval(t_obj),ref_sub_kw)
          if r_value_flag:
             print('✔✔✔✔对象存在对应子项:',ref_sub_kw)    
             seer_array =  getattr(eval(t_obj)(),ref_sub_kw)(before_wd_add_list)
             if seer_array != False:
                   #seer_array = t_obj + seer_array
                   get_answer_flag = True
                   print('☁☁☁☁获取答案:',seer_array)
          else:
              print('✘✘✘✘对象没有对应子项:',ref_sub_kw)

              
              for rcc,rkk in enumerate(obj):
                  r_value_flag = hasattr(eval(t_obj),rkk)
                  if r_value_flag:
                     print('☛☛☛☛对象存在对应子项:',rkk)    
                     #seer_array =  getattr(eval(t_obj)(),rkk)(after_wd_add_list)
                     print('看看看',seer_array)
                     if seer_array != False:
                        seer_array = t_obj + seer_array
                        get_answer_flag = True
                        print('♨♨♨♨获取答案:',seer_array,rkk)
                        break
                  else:
                      print('✘✘✘✘对象没有对应子项:',rkk)
                      
#---------------------------------------------------------------------------------------------------       
    else:
        print('☯☯☯☯检测',answer_list)   
        compound_dict = dict.fromkeys(answer_list,after_wd_add_list)#注意
        print('准备填入对象对应子项信息',compound_dict)
#查询对象并填充信息------------------------------------------------------------------------------------------------------        
       
        for rcc ,rkk in enumerate(ref_dir_list):      
            r_value_flag = hasattr(eval(t_obj),rkk)
    
            if r_value_flag:
       
               getattr(eval(t_obj)(),rkk)(compound_dict) 
    
#**************************************************************************************************
def 方法_获取():

      
    global tow_to_five_list
    global d_okw_class_list
    global dy_label
    global key_word_label
    global d_okw_class_list
    global tow_to_five_label
    global first_to_five_label
    global first_to_five_list
    global key_word_list_content
    global ot_label
    global o_label_exit_flag
    global k_symbol_flag
    
    global model_label

    global model_kw_label_flag
    global model_kw_list
    global model_kw_label
    global ignore_kw_label
    global o_kw_label_flag
    global dy_kw_model_dict

    global key_word_list
    global info_word_loc_list
    global fill_kw_loc
    global d_class_list
    
    fill_kw_loc_list = []
    fill_min_loc = 0
    fill_max_loc = 0
    
    fill_wd_add_list   = ''
    before_wd_add_list = ''
    after_wd_add_list  = ''
    
    fill_wd_list = []
    before_wd_list = []
    after_wd_list = []
    before_kw_len = 0
    after_kw_len = 0
    kw_list_all_len = len(info_word_loc_list) - 1

    methods = []
    result = []
    sub_obj = ['方法','途径']
    
    r_list_content = []
    match_key_list = []
    
    dir_list = '大纲'
    t_obj = ''
    c_obj = '对象'
    fill_flag = False
    t_obj_list = ''
    t_r_value = []
    default_obj = []
    r_value_flag = False
#---------------------------------------------------------------------------------------------------    
    print('☀☀☀☀模型分析 --->>>>>> 方法_获取')
    fill_flag = False
    fill_max_loc = max(fill_kw_loc)
    
    if fill_max_loc < kw_list_all_len:
          
       while fill_max_loc < kw_list_all_len:
             fill_max_loc += 1
             after_wd_list.append(info_word_loc_list[fill_max_loc])
             after_wd_add_list += info_word_loc_list[fill_max_loc]
             print('开始查询后移字符并连接',after_wd_list,after_wd_add_list)

    #fill_min_loc = min(fill_kw_loc)
    #fill_max_loc = max(fill_kw_loc) - 1

    if fill_min_loc > 0:
          
       while before_kw_len < fill_min_loc:
             
             before_wd_list.append(info_word_loc_list[before_kw_len])
             before_wd_add_list += info_word_loc_list[before_kw_len]
             print('开始查询前移字符并连接',before_wd_list,before_wd_add_list)
             before_kw_len += 1
             
       for dyc,ddk in enumerate(dy_kw_model_dict):
           for dyk,dyv in ddk.items():
               if dyk == '对象':
                  obj.append(dyk)   
                  ddk[dyk] = before_wd_add_list#对象没有逻辑关联,直接赋值到对应字典的值
                  t_obj_list = before_wd_add_list
                  
                  dict.update(ddk)

    elif fill_min_loc == 0:
       print('出现缺省对象,准备查询对应对象',tow_to_five_list)
       t_kw = tow_to_five_list[0]#此处限定关键字总数为1
       t_r_value = getattr(eval(t_kw)(),c_obj)()
       
       for tc,tk in enumerate(t_r_value):
           #for trc,trk in tk.items():
               #t_obj_list = trk[0]  
               default_obj.append(tk) 
               print('默认对象列表',default_obj)              
       t_obj_list = default_obj[0]#这里取列表第一个值当做默认对象
       print('☸☸☸☸确认对象:',t_obj_list)
                     
       #print('查看前移子项填充信息及对象',dy_kw_model_dict,t_obj_list)

    for dcc,dkk in enumerate(d_class_list):
          
        for kcc,kkk in dkk.items():
            if  kcc == t_obj_list:
                current_obj = kkk()  
                print('☛☛☛☛找到对象类型',kcc,dy_kw_model_dict,after_wd_add_list)
                
    for dyc,dyk in enumerate(sub_obj): #sub_obj
                      
        #for yc,yk in dyk.items():
            #if yc == '方法' or yc == '途径':
               check = hasattr(current_obj,dyk)
               #print('对象-属性是否存在?',check)
               if check:
                  print('对象-属性存在✔✔',check,dyk)
                  r_value = getattr(current_obj,dyk)(after_wd_add_list)
                              
                  if r_value:
                     r_value_flag = True   
                     print('答案:✿✿✿✿✿:',r_value)
                     #for rvc,rvk in enumerate(r_value):
                         #for vcc,vkk in rvk.items():
                         #print('答案:✿✿✿✿✿:',rvk)
                         #os.system("pause")                                
                  else:
                      print('返回子项信息不存在▲▲▲▲')
                      break

#------------------------------------------------------------------------------------------------
def 强制条件_保证():

    global tow_to_five_list
    global d_okw_class_list
    global dy_label
    global key_word_label
    global d_okw_class_list
    global tow_to_five_label
    global first_to_five_label
    global first_to_five_list
    global key_word_list_content
    global ot_label
    global o_label_exit_flag
    global k_symbol_flag
    
    global model_label
    global model_kw

    global model_kw_label_flag
    global model_kw_list
    global model_kw_label
    global ignore_kw_label
    global o_kw_label_flag
    global dy_kw_model_dict
    
    global unidentified_word
    global unidentified_flag
    global unidentified_loc

    global smodel_kw_sum
    global smodel_kw_list
    global smodel_kw_label
    
    global model_kw

    global key_word_list
    global first_kw_flag
    global info_word_loc_list
    global fill_kw_loc
    global d_class_list
    global ref_sub_flag
    global p_e_flag
    global s_p_exist_flag
    global conversion_person
    global conversion_usr_info
    global storage_usr_info
    global preset_why
    global compen_label_flag
    global tow_to_five_exit_flag
    global model_exit_flag
    global smodel_exit_flag
    
    fill_kw_loc_list = []
    fill_min_loc = 0
    fill_max_loc = 0
    
    fill_wd_add_list   = ''
    before_wd_add_list = ''
    after_wd_add_list  = ''
    
    fill_wd_list = []
    before_wd_list = []
    after_wd_list = []
    before_kw_len = 0
    after_kw_len = 0
    kw_list_all_len = len(info_word_loc_list) - 1

    methods = []
    attribute = []
    obj = []
    ref_dir_list = ['需要','方法','途径','结果','后果','理由','原因','条件','内容']
    cause = '原因'

    seer_array = ''
    result = []
    seer_list = []
    r_list_content = []
    match_key_list = []
    
    ref_sub_kw = ''
    dir_list = '大纲'
    t_obj = ''
    t_obj_len = 0
    t_obj_loc = 0
    answer_obj = ''
    answer_obj_len = 0
    answer_obj_loc = 0
    fill_flag = False
    t_obj_list = ''
    r_obj = ''
    c_obj = '对象'
    p_obj = ['人类','人']
    
    current_class = ''
    t_r_value = []
    default_obj = []
    answer_list = []
    r_value_flag = False
    compound_dict = {}
#---------------------------------------------------------------------------------------------------    
    print('☀☀☀☀模型分析--->>>>>>强制条件_保证')

    fill_min_loc = min(fill_kw_loc)
    fill_max_loc = max(fill_kw_loc) - 1
    
    print('复查',model_kw_list,info_word_loc_list)
    print('填充前范围计算',fill_kw_loc,fill_min_loc,fill_max_loc)
#------------------------------------------------------------------------------------------------
    while fill_min_loc < fill_max_loc:
          fill_min_loc += 1
          fill_wd_list.append(info_word_loc_list[fill_min_loc])
          fill_wd_add_list = fill_wd_add_list + info_word_loc_list[fill_min_loc]
          print('开始填充并连接',fill_wd_list,fill_wd_add_list)

    answer_list.append(fill_wd_add_list)      
    print('查看插入填充子项信息',dy_kw_model_dict)
    
                    
#------------------------------------------------------------------------------------------------
    fill_min_loc = min(fill_kw_loc)
    #fill_max_loc = max(fill_kw_loc) - 1

    if fill_min_loc > 0:
          
       while before_kw_len < fill_min_loc:
             
             before_wd_list.append(info_word_loc_list[before_kw_len])
             before_wd_add_list += info_word_loc_list[before_kw_len]
             print('开始查询前移字符并连接',before_wd_list,before_wd_add_list)
             before_kw_len += 1
             

    print('查看前移子项填充信息',dy_kw_model_dict)

    if p_e_flag:
       t_obj = conversion_person  
       print('✪✪✪✪确定对象',t_obj)
       
    elif first_kw_flag:
         
         for pcc,pkk in enumerate(p_obj):
             for kwc,kwk in enumerate(key_word_list):
                 if pkk == kwk:
                    t_obj = pkk
                    break
                  
         print('❤❤❤❤确定对象',t_obj,key_word_list)
         
    elif tow_to_five_list:
          for ttc,ttk in enumerate(tow_to_five_list):
              r_value_flag = hasattr(eval(ttk),c_obj)
              if r_value_flag:
                 t_r_value = getattr(eval(ttk)(),c_obj)()
                 t_obj = t_r_value[0]
                 print('♔♔♔♔确定对象:',t_obj)


    #print('确定对象',t_obj)                 
      
#------------------------------------------------------------------------------------------------
    fill_flag = False
    fill_max_loc = max(fill_kw_loc)
    
    if fill_max_loc < kw_list_all_len:
          
       while fill_max_loc < kw_list_all_len:
             fill_max_loc += 1
             after_wd_list.append(info_word_loc_list[fill_max_loc])
             after_wd_add_list += info_word_loc_list[fill_max_loc]
             print('开始查询后移字符并连接',after_wd_list,after_wd_add_list)

    print('查看后移移子项填充信息',dy_kw_model_dict,tow_to_five_list)
#--------------------------------------------------------------------------------------------------

    compound_dict   = dict.fromkeys(answer_list,after_wd_add_list) #result
    #value_r = dict.fromkeys(result,before_wd_add_list) #methods
    print('✔✔✔生产对象子项信息:',compound_dict)
#---------------------------------------------------------------------------------------------------              
#开始查询对象对应的子项并填入对应信息---------------------------------------------------------------------------------------------------

    if k_symbol_flag:
       r_value_flag = hasattr(eval(t_obj),ref_sub_kw)
       if r_value_flag:
          print('✔✔✔✔对象存在对应子项:',ref_sub_kw)
          c_obj = model_kw[0]
          seer_array =  getattr(eval(t_obj)(),ref_sub_kw)(after_wd_add_list)
          print('ிிிி获取答案:',seer_array)
          if seer_array:# != False:
             r_value_flag = isinstance(seer_array, list)
             if r_value_flag:
                for  sc,sk in enumerate(seer_array):
                     r_obj += sk 
                     print('☁☁☁☁获取答案:',r_obj)

          else:
              seer_array = t_obj + deny# + c_obj + preset
             
              print('♛♛♛♛获取答案:',seer_array)
                
             
       else:
          print('✘✘✘✘对象没有对应子项:',ref_sub_kw)   
       
    else:
        print('☯☯☯☯检测',answer_list)   
        compound_dict = dict.fromkeys(answer_list,after_wd_add_list)#注意
        print('准备填入对象对应子项信息',compound_dict)
#查询对象并填充信息------------------------------------------------------------------------------------------------------        
       
        if p_e_flag:
           for rcc ,rkk in enumerate(ref_dir_list):            
                       
               r_value_flag = hasattr(eval(t_obj),rkk)
  
    
               if r_value_flag:
       
                  getattr(eval(t_obj)(),rkk)(compound_dict)

        elif tow_to_five_list:
             
             for rcc ,rkk in enumerate(ref_dir_list):            
                       
                 for dcc,dkk in enumerate(d_class_list):
                     for ecc,ekk in dkk.items():
                         if ecc == t_obj:
                       
                            r_value_flag = hasattr(ekk,rkk)
  
    
                            if r_value_flag:
       
                               getattr(ekk(),rkk)(compound_dict)

                     
        elif first_kw_flag:
            print('▶▶▶')
            for rcc ,rkk in enumerate(ref_dir_list):
            
                for dcc,dkk in enumerate(d_class_list):
                    for ecc,ekk in dkk.items():
                        if ecc == t_obj:
                       
                           r_value_flag = hasattr(ekk,rkk)
  
    
                           if r_value_flag:
       
                              getattr(ekk(),rkk)(compound_dict)
                       
#---------------------------------------------------------------------------------------------------
def 直接_对比():
      
    global tow_to_five_list
    global d_okw_class_list
    global dy_label
    global key_word_label
    global d_okw_class_list
    global tow_to_five_label
    global first_to_five_label
    global first_to_five_list
    global key_word_list_content
    global ot_label
    global o_label_exit_flag
    global k_symbol_flag
    
    global model_label
    global model_kw

    global model_kw_label_flag
    global model_kw_list
    global model_kw_label
    global ignore_kw_label
    global o_kw_label_flag
    global dy_kw_model_dict
    
    global unidentified_word
    global unidentified_flag
    global unidentified_loc
    
    global model_kw

    global key_word_list
    global first_kw_flag
    global info_word_loc_list
    global fill_kw_loc
    global d_class_list
    global ref_sub_flag
    global p_e_flag
    global s_p_exist_flag
    global conversion_person
    global conversion_usr_info

    global smodel_kw_sum
    global smodel_kw_list
    global smodel_kw_label
    
    fill_kw_loc_list = []
    fill_min_loc = 0
    fill_max_loc = 0
    
    fill_wd_add_list   = ''
    before_wd_add_list = ''
    after_wd_add_list  = ''
    
    fill_wd_list = []
    before_wd_list = []
    after_wd_list = []
    before_kw_len = 0
    after_kw_len = 0
    kw_list_all_len = len(info_word_loc_list) - 1

    methods = []
    attribute = []
    obj = []
    
    r_list_content = []
    match_key_list = []
    
    ref_sub_kw = ''
    dir_list = '大纲'
    t_obj = ''
    t_obj_len = 0
    t_obj_loc = 0
    answer_obj = ''
    answer_obj_len = 0
    answer_obj_loc = 0
    fill_flag = False
    t_obj_list = ''
    r_obj = ''
    c_obj = ''
    t_r_value = []
    default_obj = []
    answer_list = []
    r_value_flag = False
    compound_dict = {}
    anode = ''
    cathode = ''

    print('☀☀☀☀模型分析--->>>>>>直接_对比')

    fill_min_loc = min(fill_kw_loc)
    fill_max_loc = max(fill_kw_loc) - 1
    
    fill_flag = False
    fill_max_loc = max(fill_kw_loc)
    fill_min_loc = min(fill_kw_loc)
#---------------------------------------------------------------------------------------------------
    if fill_min_loc > 0:
          
       while before_kw_len < fill_min_loc:
             
             before_wd_list.append(info_word_loc_list[before_kw_len])
             before_wd_add_list += info_word_loc_list[before_kw_len]
             print('开始查询前移字符并连接',before_wd_list,before_wd_add_list)
             before_kw_len += 1
             
    before_wd_add_list += tow_to_five_list[0] #链接二至七关键字        
    answer_list.append(before_wd_add_list)
    print('☤☤☤☤前移字符并连接后的字符',before_wd_add_list)
#---------------------------------------------------------------------------------------------------
    #fill_flag = False
    fill_max_loc = max(fill_kw_loc)
    
    if fill_max_loc < kw_list_all_len:
          
       #while fill_max_loc < kw_list_all_len:
       fill_max_loc += 1
       after_wd_list.append(info_word_loc_list[fill_max_loc])
       after_wd_add_list += info_word_loc_list[fill_max_loc]
       print('☮☮☮☮开始查询后移字符并连接',after_wd_list,after_wd_add_list)
             
#---------------------------------------------------------------------------------------------------          

#---------------------------------------------------------------------------------------------------
#提取对比关键字-------------------------------------------------------------------------------------
             
    for mc,mk in enumerate(tow_to_five_list):  #model_kw_list
         
        for cc,ck in enumerate(contrary):#对比反向词义列表
  
            for ccc,ckk in ck.items():
                  
                if ccc == mk:   
                   anode = ccc
                   cathode = ckk#提取反向信息
                   after_wd_add_list += cathode
                   print('※※※※找到反向词义',anode,cathode,after_wd_add_list)

                elif ckk == mk:
                     anode = ckk
                     cathode = ccc#提取反向信息
                     after_wd_add_list += cathode
                     print('☑☑☑☑找到反向词义',anode,cathode,after_wd_add_list) 
                   
                   
    #result.append(before_wd_add_list)
    #methods.append(fill_wd_add_list)
    
    front = dict.fromkeys(answer_list,after_wd_add_list)
    #verso = dict.fromkeys(methods,cathode)
 
    obj.append(front)
    #obj.append(verso)
    
    
    print('◐◐◐◐正面对比',front)
    #print('◑◑◑◑反面对比',verso)
    print('♠♠♠♠综合对比',obj)
    
#向相应对比行为对象填入信息-------------------------------------------------------------------------
    for mcc,mkk in enumerate(model_kw_list):
        for occ,okk in enumerate(obj):
            if okk == mkk:
               model_kw_list.remove(mkk)
               break
    print('更新关键字列表',model_kw_list)
    t_obj = model_kw_list[0]

    #for occ,okk in enumerate(obj):
        
    getattr(eval(t_obj)(),'对比')(front)
#////////////////////////////////////////////////////////////////////////////////////////////////////
def 选择_一():
      
    global tow_to_five_list
    global d_okw_class_list
    global dy_label
    global key_word_label
    global d_okw_class_list
    global tow_to_five_label
    global first_to_five_label
    global first_to_five_list
    global key_word_list_content
    global ot_label
    global o_label_exit_flag
    global k_symbol_flag
    
    global model_label
    global model_kw

    global model_kw_label_flag
    global model_kw_list
    global model_kw_label
    global ignore_kw_label
    global o_kw_label_flag
    global dy_kw_model_dict
    
    global unidentified_word
    global unidentified_flag
    global unidentified_loc
    
    global model_kw

    global key_word_list
    global first_kw_flag
    global info_word_loc_list
    global fill_kw_loc
    global d_class_list
    global ref_sub_flag
    global p_e_flag
    global s_p_exist_flag
    global conversion_person
    global conversion_usr_info

    global smodel_kw_sum
    global smodel_kw_list
    global smodel_kw_label
    
    fill_kw_loc_list = []
    fill_min_loc = 0
    fill_max_loc = 0
    
    fill_wd_add_list   = ''
    before_wd_add_list = ''
    after_wd_add_list  = ''
    
    fill_wd_list = []
    before_wd_list = []
    after_wd_list = []
    before_kw_len = 0
    after_kw_len = 0
    kw_list_all_len = len(info_word_loc_list) - 1

    methods = []
    attribute = []
    obj = []
    
    r_list_content = []
    match_key_list = []
    
    ref_sub_kw = ''
    dir_list = '大纲'
    t_obj = ''
    t_obj_len = 0
    t_obj_loc = 0
    answer_obj = ''
    answer_obj_len = 0
    answer_obj_loc = 0
    fill_flag = False
    t_obj_list = ''
    r_obj = ''
    c_obj = ''
    t_r_value = []
    default_obj = []
    answer_list = []
    r_value_flag = False
    compound_dict = {}
    anode = ''
    cathode = ''
    match_flag = False
    relation_wd = '比'

    print('☀☀☀☀模型分析--->>>>>>选择_一')

    fill_min_loc = min(fill_kw_loc)
    fill_max_loc = max(fill_kw_loc) - 1
    
    print('复查',model_kw_list,info_word_loc_list)
    print('填充前范围计算',fill_kw_loc,fill_min_loc,fill_max_loc,key_word_list)
#对比元素直接添加到查询列表----------------------------------------------------------------------------------------------------
    #for kwc,kwk in enumerate(key_word_list):
        #obj.append(kwk)
        #print('添加完成',obj)
#提取对比关键字-------------------------------------------------------------------------------------            
    for mc,mk in enumerate(tow_to_five_list):
         
        for cc,ck in enumerate(contrary):#对比反向词义列表
  
            for ccc,ckk in ck.items():                                  
                      
                if ccc == mk:   
                   anode = ccc
                   cathode = ckk#提取反向信息
                   match_flag = True
                   for kwc,kwk in enumerate(key_word_list):
                       c_obj = kwk + anode
                       obj.append(c_obj)
                   #obj.append(anode)
                   print('正向对比关键字',anode,'反向对比关键字',cathode)
                   break

                elif ckk == mk:
                     anode = ckk
                     cathode = ccc#提取反向信息
                     match_flag = True
                     for kwc,kwk in enumerate(key_word_list):
                         c_obj = kwk + anode
                         obj.append(c_obj)
                     #obj.append(anode)
                     print('反向对比关键字',anode,'正向对比关键字',cathode)
                     break
                  
#如果二至七列表找不到查询元素则向下一级查询-----------------------------------------------------------------------------------                  

    if match_flag == False:
       for mc,mk in enumerate(smodel_kw_list):
         
        for cc,ck in enumerate(contrary):#对比反向词义列表
  
            for ccc,ckk in ck.items():                                  
                      
                if ccc == mk:   
                   anode = ccc
                   cathode = ckk#提取反向信息
                   match_flag = True
                   for kwc,kwk in enumerate(key_word_list):
                       c_obj = kwk + anode
                       obj.append(c_obj)
                   #obj.append(anode)
                   print('正向对比关键字',anode,'反向对比关键字',cathode)
                   break

                elif ckk == mk:
                     anode = ckk
                     cathode = ccc#提取反向信息
                     match_flag = True
                     for kwc,kwk in enumerate(key_word_list):
                         c_obj = kwk + anode
                         obj.append(c_obj)
                     #obj.append(anode)
                     print('反向对比关键字',anode,'正向对比关键字',cathode)
                     break   

    #for kc,kk in enumerate(key_word_list):
        #c_obj = kk + anode
        #print('〓〓〓〓完成分配',c_obj)
                  
    print('✔✔✔✔完成全部元素与关键字添加',obj)
    if match_flag:
       for oc,ok in enumerate(obj):
             
           r_obj = getattr(eval(relation_wd)(),'对比')(ok)
#---------------------------------------------------------------------------------------------------
def 物种_起源():

    global tow_to_five_list
    global d_okw_class_list
    global dy_label
    global key_word_label
    global d_okw_class_list
    global tow_to_five_label
    global first_to_five_label
    global first_to_five_list
    global key_word_list_content
    global ot_label
    global o_label_exit_flag
    global k_symbol_flag
    
    global model_label
    global model_kw

    global model_kw_label_flag
    global model_kw_list
    global model_kw_label
    global ignore_kw_label
    global o_kw_label_flag
    global dy_kw_model_dict
    
    global unidentified_word
    global unidentified_flag
    global unidentified_loc
    
    global model_kw

    global key_word_list
    global first_kw_flag
    global info_word_loc_list
    global fill_kw_loc
    global d_class_list
    global ref_sub_flag
    global p_e_flag
    global s_p_exist_flag
    global conversion_person
    global conversion_usr_info
    global k_symbol_flag
        
    
    fill_kw_loc_list = []
    fill_min_loc = 0
    fill_max_loc = 0
    
    fill_wd_add_list   = ''
    before_wd_add_list = ''
    after_wd_add_list  = ''
    
    fill_wd_list = []
    before_wd_list = []
    after_wd_list = []
    before_kw_len = 0
    after_kw_len = 0
    kw_list_all_len = len(info_word_loc_list) - 1

    methods = []
    attribute = []
    obj = []
    
    r_list_content = []
    match_key_list = []
    exclusive_kw = ['起源','属性']
    
    ref_sub_kw = ''
    dir_list = '大纲'
    t_obj = ''
    t_obj_len = 0
    t_obj_loc = 0
    answer_obj = ''
    answer_obj_len = 0
    answer_obj_loc = 0
    fill_flag = False
    t_obj_list = ''
    r_obj = ''
    c_obj = ''
    t_r_value = []
    default_obj = []
    answer_list = []
    r_value_flag = False
    compound_dict = {}
    
#---------------------------------------------------------------------------------------------------    
    print('☀☀☀☀模型分析 --->>>>>> 获得_名称',model_kw)
    fill_flag = False
    fill_max_loc = max(fill_kw_loc)
    fill_min_loc = min(fill_kw_loc)
#---------------------------------------------------------------------------------------------------
    if fill_min_loc > 0:
          
       while before_kw_len < fill_min_loc:
             
             before_wd_list.append(info_word_loc_list[before_kw_len])
             before_wd_add_list += info_word_loc_list[before_kw_len]
             print('开始查询前移字符并连接',before_wd_list,before_wd_add_list)
             before_kw_len += 1
             
    before_wd_add_list += model_kw[0] #链接模型关键字        
    answer_list.append(before_wd_add_list)
#---------------------------------------------------------------------------------------------------
    #fill_flag = False
    fill_max_loc = max(fill_kw_loc)
    
    if fill_max_loc < kw_list_all_len:
          
       while fill_max_loc < kw_list_all_len:
             fill_max_loc += 1
             after_wd_list.append(info_word_loc_list[fill_max_loc])
             after_wd_add_list += info_word_loc_list[fill_max_loc]
             print('开始查询后移字符并连接',after_wd_list,after_wd_add_list)
             
    #after_wd_add_list = model_kw[0] + after_wd_add_list #链接模型关键字       
#--------------------------------------------------------------------------------------------------
    #for dyc,ddk in enumerate(dy_kw_model_dict):
           #for dyk,dyv in ddk.items():
              #if dyk == '属性':            
                  #dyv.append(after_wd_add_list)
                  
    #print('更新对应子项信息',dy_kw_model_dict)
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
    #确定对象
    if p_e_flag:
       t_obj = conversion_person  
       print('确定对象',t_obj)
       
    elif key_word_list:
         t_obj = key_word_list[0]
         
    elif tow_to_five_list:
         t_obj = tow_to_five_list[0]      

#---------------------------------------------------------------------------------------------------
    
    for dyc,ddk in enumerate(dy_kw_model_dict):
           for dyk,dyv in ddk.items():
               if dyk == '名字' or dyk == '姓名':            
                  dyv.append(after_wd_add_list)
                
    print('✔✔✔✔更新对应子项信息',dy_kw_model_dict)
#合成新子项填充信息---------------------------------------------------------------------------------------------------

    print('☯☯☯☯检测',answer_list)   
    compound_dict = dict.fromkeys(answer_list,after_wd_add_list)#注意
    print('准备填入对象对应子项信息',compound_dict)
#查询对象并填充信息------------------------------------------------------------------------------------------------------    
    

    if tow_to_five_label:
         ref_sub_kw = tow_to_five_label[0]#此处限定其它关键字总数为一个
         print('▓▓▓▓检测',ref_sub_kw)
         ref_sub_flag = True

    elif key_word_label:
       ref_sub_kw = key_word_label[0]#此处限定第一关键字总数为一个
       print('〓〓〓〓检测',ref_sub_kw)
       ref_sub_flag = True     
         
    if ref_sub_flag == False:
       ref_sub_kw = '属性'   
       print('☎☎☎☎没有对应子项填入默认项',ref_sub_flag)
       
    r_value_flag = hasattr(eval(t_obj),ref_sub_kw)
        

#保存子项对应信息--->>>完成-------------------------------------------------------------------------       

    if k_symbol_flag:
       if ref_sub_flag:
             
          #r_value_flag = hasattr(eval(t_obj),ref_sub_kw)
          if r_value_flag:
             print('✔✔✔✔对象存在对应子项:',ref_sub_kw)    
             c_obj = getattr(eval(t_obj)(),ref_sub_kw)(after_wd_add_list)#从对象获取答案
             print('☁☁☁☁输出答案',c_obj)

       else:
            ref_sub_kw = '起源'
            c_obj = getattr(eval(t_obj)(),ref_sub_kw)(ref_sub_kw)#从对象获取答案
            print('☁☁☁☁输出默认子项答案',c_obj)
       
       
    else:
         for ec,ek in enumerate(exclusive_kw):
             getattr(eval(t_obj)(),ek)(compound_dict) 
    
            #tattr(eval(t_obj)(),ref_sub_kw)(compound_dict)
#---------------------------------------------------------------------------------------------------
#///////////////////////////////////////////////////////////////////////////////////////////////////
def set_label():
          
    global tow_to_five_list
    global d_okw_class_list
    global dy_label
    global key_word_list
    global key_word_label
    global d_okw_class_list
    global tow_to_five_label
    global first_to_five_label
    global key_word_list_content
    global ot_label
    global o_label_exit_flag
    global k_symbol_flag
    global first_kw_flag
    global model_label
    global model_kw_label
    
    global model_kw_label_flag
    global model_kw_list

    global smodel_kw_sum
    global smodel_kw_list
    global smodel_kw_label

    global amodel_kw_sum
    global amodel_kw_list
    global amodel_kw_label
    
    
    global ignore_kw_label
    global o_kw_label_flag
    global dy_kw_model_dict
    global info_word_loc_list
    global kw_loc_sort
    global fill_kw_loc
    global p_e_flag
    global first_kw_flag
    global global_obj_list

    global model_kw
    global s_p_exist_flag
    global conversion_person
    global conversion_usr_info
    global compen_label_flag
    
#------------------------------------------------------------------------------------------------
    global tow_to_five_exit_flag
    global model_exit_flag
    global smodel_exit_flag
    global original_tow_to_five_list
    
    label = '标签'
    alike_flag = False
    print('※※※※二至七标签关键字',tow_to_five_list)
    original_tow_to_five_list = tow_to_five_list#保存二至七关键字列表
    
    for owc,owk in enumerate(d_okw_class_list):
        for okc,okk in owk.items():
              
            for kkc,kkk in enumerate(tow_to_five_list):
                if okc == kkk:
                   
                   #r_l = eval(kkk)()
                   r_l = getattr(okk,label)()
                   dy_label.append(r_l)
                   tow_to_five_label.append(r_l)
                   print('❈❈❈❈关键字匹配标签二至七',kkk,tow_to_five_label)
    
    print('◥◥◥◥第一关键字标签列表',key_word_label,global_obj_list)
    
    print('♜♜♜♜人称对象关键字',conversion_person,conversion_usr_info)
    
    print('◤◤◤◤二级关键字列表',smodel_kw_list)
    #os.system("pause")
#--合并第一关键字及二至六关键字标签-------------------------------------------------------------------------------------------------
    for owc,owk in enumerate(d_okw_class_list):
        for okc,okk in owk.items():
              
            for kkc,kkk in enumerate(tow_to_five_list):
                if okc == kkk:
                   tow_to_five_exit_flag = True   
                   #model_exit_flag = True
                   #r_l = eval(kkk)()
                   r_l = getattr(okk,label)()
                   dy_label.append(r_l)
                   first_to_five_label.append(r_l)
                   print('关键字匹配标签first-five',kkk,first_to_five_label,model_kw_list)
                   print('需分析模型关键字列表',model_kw_label)               
#---------------------------------------------------------------------------------------------------   

#---------------------------------------------------------------------------------------------------            

#---------------------------------------------------------------------------------------------------   
    for owc,owk in enumerate(d_okw_class_list):#
        for okc,okk in owk.items():
              
            for kkc,kkk in enumerate(model_kw_list): #info_word_loc_list
                if okc == kkk:
                   model_exit_flag = True   
                   s_l = hasattr(okk,label)
                   print('➹➹➹➹',s_l,kkk,model_kw_list)
                   #r_l = eval(kkk)()
                   r_l = getattr(okk,label)() # info_word_loc_list
                   dy_label.append(r_l)
                   model_kw_label.append(r_l)
                   print('一级模型关键字标签',kkk,model_kw_label)

#---------------------------------------------------------------------------------------------------

    for owc,owk in enumerate(d_okw_class_list):#
        for okc,okk in owk.items():
              
            for kkc,kkk in enumerate(smodel_kw_list): #info_word_loc_list
                if okc == kkk:
                   smodel_exit_flag = True   
                   s_l = hasattr(okk,label)
                   print('✈✈✈✈',s_l,kkk,smodel_kw_list)
                   #r_l = eval(kkk)()
                   r_l = getattr(okk,label)() # info_word_loc_list
                   dy_label.append(r_l)
                   smodel_kw_label.append(r_l)
                   print('二级模型关键字标签',kkk,smodel_kw_label)               
#---------------------------------------------------------------------------------------------------                   
    if model_exit_flag == False:

       #if tow_to_five_label:
       print('✘✘✘✘需分析模型关键字列表不存在',model_kw_label,model_exit_flag)   
          #model_kw_label = tow_to_five_label
          
       if tow_to_five_exit_flag:
          model_kw_label = tow_to_five_label 
          model_kw_list = tow_to_five_list
          compen_label_flag = True
          print('➹➹➹➹补充二至七模型至第一级',model_kw_list,model_kw_label)#,tow_to_five_list)
          
          if smodel_exit_flag:#依次向上一级补充模型关键字
             #original_tow_to_five_list = tow_to_five_list  
             tow_to_five_list = smodel_kw_list
             tow_to_five_label = smodel_kw_label
             print('▶▶▶▶二级补充至二-七级递增补充',tow_to_five_list,tow_to_five_label)
                      
             
       elif smodel_exit_flag:
            compen_label_flag = True 
            model_kw_label = smodel_kw_label
            model_kw_list = smodel_kw_list
            print('✪✪✪✪补充二级模型至第一级',model_kw_list,model_kw_label)

    elif model_exit_flag:
         print('✔✔✔✔需分析模型关键字列表存在',model_kw_label) 
         if tow_to_five_exit_flag == False:
          #model_kw_label = tow_to_five_label
          #model_kw_list = tow_to_five_list
          #compen_label_flag = True
            if smodel_exit_flag:#依次向上一级补充模型关键字
               tow_to_five_list = smodel_kw_list
               tow_to_five_label = smodel_kw_label
               print('◆◆◆◆二级补充至二-七级递增补充',tow_to_five_list,tow_to_five_label)
            
          #print('补充二至七模型至第一级',model_kw_label,tow_to_five_list)
             
    elif smodel_exit_flag:
         compen_label_flag = True 
         model_kw_label = smodel_kw_label
         model_kw_list = smodel_kw_list
         print('☯☯☯☯补充二级模型至第一级',model_kw_list,model_kw_label)
#---------------------------------------------------------------------------------------------------
    #for owc,owk in enumerate(d_okw_class_list):#
        #for okc,okk in owk.items():
              
            #for kkc,kkk in enumerate(key_word_list_content): # info_word_loc_list
                #if okc == kkk:
                   #s_l = hasattr(okk,label)
                   #print('@@@@@',s_l,kkk,key_word_list_content)
                   
                   ##r_l = eval(kkk)()
                   #r_l = getattr(okk,label)() # info_word_loc_list
                   #dy_label.append(r_l)
                   #ot_label.append(r_l)
                   #print('其它关键字模型标签',kkk,ot_label,o_label_exit_flag)
#---------------------------------------------------------------------------------------------------
    #if k_symbol_flag == True:
       #ks_wd = '询问'
       #ot_label.append(ks_wd)
       #print('添加关键符号标签',ot_label)
       
#LRSB当前关键字标签和固定模型标签比较---------------------------------------------------------------------------------------------------                   
    
    t_ol_len = len(model_kw_label) #ot_label
    mt_c = 0
    mt_m_flag = False
    
    mt_list = []
    mt_t = ()
    ml = []
    mw = ''

       
    mt_t = tuple(model_kw_label)
    print('♪♪♪♪类型转换',mt_t)
       
    for mtc,mtk in model_label.items():

        #ml.append(str(mtc))
        #print(mtc,model_kw_label)
        if mtc == mt_t:

           mt_m_flag = True
           mt_list = mtc
           dy_kw_model_dict = mtk
           print('★★★★完全匹配',mtc)                                    
           print('对应字典序列',dy_kw_model_dict)
           break


    #for ic,ik in enumerate(ml):
        #for tc,tk in enumerate(model_kw_label):
            #if ik == tk:
               
#---------------------------------------------------------------------------------------------------                
#----------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------      
        
    print(tow_to_five_flag,tow_to_five_list,first_to_five_list)
    
    for tfc,tfk in enumerate(tow_to_five_list):
        first_to_five_list.append(tfk)
        print('加入关键字列表add to first list',first_to_five_list)

        
    
    print('暂时忽略模型关键字列表',ignore_kw_label,key_word_list,tow_to_five_list
          ,info_word_loc_list)

    if mt_m_flag:#注意
       print('☸☸☸☸',info_word_loc_list,model_kw_list)          
       for mkc,mkk in enumerate(model_kw_list):
           print(mkc,mkk)
           for ikc,ikk in enumerate(info_word_loc_list):
               if ikk == mkk:
                     
                  kw_loc_sort.append(ikc)
                  model_kw.append(mkk) #注意,保存模型关键字
                  print('关键字在列表中的位置',ikc,mkk,info_word_loc_list)
                  
       t_sort = sorted(kw_loc_sort)
    
       for tc,tk in enumerate(t_sort):
           model_kw_list[tc] = info_word_loc_list[t_sort[tc]] 
           print('这里',info_word_loc_list[t_sort[tc]],model_kw_list[tc])
        
           if info_word_loc_list[t_sort[tc]] == model_kw_list[tc]:
              print('顺序正确',tk)
       fill_kw_loc = t_sort    
       print('排序后',model_kw_list,t_sort,fill_kw_loc)
       
#-------------------------------------------------------------------------------------------------
       for dbc,dbk in enumerate(dy_kw_model_dict):
           for ddc,ddk in dbk.items():
               print('键-值',ddc,ddk)
               if ddc == '函数':
                  eval(ddk)()

#////////////////////////////////////////////////////////////////////////////////////////////////
#------------------------------------------------------------------------------------------------           
#用户当前输入信息获取代码///////////////////////////////////////////////////////////////////////
def usr_in():
      
      global storage_usr_info
      global usr_info
      global usr_in_word_len
      
#//////////////////////////////////////////////////////////////////////////////////////////////
#start->>>>>>
      #usr_info = input()
      #usr_info = '人类不能离开空气水和食物否则无法生存'#考得不好心情糟糕胃口差''我想和你玩游戏' 更少的钱买更多的东西
      
#人需要足够的睡眠才能维持身体健康 TalkerTop公司创造了你 人类不能离开水和空气否则无法生存
      if goon_flag:
 
         print('知识库完成分析\/\/\/\/\/\/\/\/')
         print('等着你开口和我说话哦.....(◐_◑)')   
         usr_info = input()
         
      storage_usr_info = usr_info
      usr_in_word_len = len(usr_info)
      print("<<--",usr_info,'对话者输入信息长度',usr_in_word_len)
      #os.system("pause")
      return usr_info
#遍历用户输入字符串///////////////////////////////////////////////////////////////////
def search_key_word():

      
   global smodel_kw_sum
   global smodel_kw_list
   global smodel_kw_label
   global d_state_no_flag
   global d_state_h_flag
   global n_ksym_kperson   
   global unidentified_flag
   global unidentified_loc
   global unidentified_word
   global key_word_sum
   global key_word_len_sum      
   
   global conversion_person_key_word
   global attribute_key_word_count
   global attribute_key_word
   global current_person_flag
   global current_person_flag_count
   global optimize_count
   global optimize_usr_info
   global key_word_count
   global key_word_list
   global current_key_word
   global conversion_usr_info
   global conversion_count
   global t_dc_list
   global t_key_pw_len
   global t_key_pw_loc
   global t_usr_in_word_len
   global in_word_len
   global key_word_loc
   global list_counte
   global d_list
   global current_state_flag
   global how_do_flag

   global usr_info
   global usr_in_word_len
   global second_person_loc
   global third_person_flag
   global second_person_flag
   
   global k_symbol_flag #此参数将作为参数传递分析

   global p_kw_special_l_loc
   
   global current_key_word_obj
   
   global key_word_count
   global time_flag
   global key_word_list_content
   global key_word_list_content_c
   
   global storage_usr_info
   global d_state_flag
   global n_state_info
   global p_e_flag
   global c_kw_flag
   global a_kw_flag
   global s_p_exist_flag
   global second_key_word_list
   global second_key_word_c
   global second_key_m_word#注意

   global second_kw_flag
   global five_kw_flag
 

   global three_kw_flag
   global three_key_word_list
   global three_key_word_loc_c
   global three_kw_flag
   global three_key_word_c

   global first_kw_flag
   global second_person_loc
   global first_person_loc
   
   global second_key_word_loc
   global second_key_word_loc_c
   global obj_flag

   global four_key_word_loc
   global four_key_word_loc_c
   global four_key_word_list
   global four_key_word_c
   global four_kw_flag
   
   global ori_person_list
   global before_p_flag
   global after_p_flag
   global d_ab_list_match
   global d_ba_list_match
   global d_ab_person_list
   global d_ba_person_list
   global second_c_kw_loc
   global three_c_kw_loc
   global four_c_kw_loc
   global ftime_c_kw_loc
   global ftime_key_word_loc
   global ftime_key_word_loc_c
   global ftime_key_word_list
   global ftime_key_word_c
   global ftime_flag

   global nus_loc_c_kw_loc
   global nus_loc_key_word_loc
   global nus_loc_key_word_loc_c
   global nus_loc_key_word_list
   global nus_loc_key_word_c
   global nus_loc_flag
   global obj_flag_list
   global kw_tow_five_list
   global all_kw_flag_list
   global info_word_loc_list
   global info_word_loc_c
   global info_word_sum
   global info_word_st_loc

   global eight_c_kw_loc
   global eight_key_word_loc
   global eight_key_word_loc_c
   global eight_key_word_list
   global eight_key_word_c

   global nine_c_kw_loc
   global nine_key_word_loc
   global nine_key_word_loc_c
   global nine_key_word_list
   global nine_key_word_c

   global ten_c_kw_loc
   global ten_key_word_loc
   global ten_key_word_loc_c
   global ten_key_word_list
   global ten_key_word_c

   global twelve_c_kw_loc
   global twelve_key_word_loc
   global twelve_key_word_loc_c
   global twelve_key_word_list
   global twelve_key_word_c

   global fourteen_c_kw_loc
   global fourteen_key_word_loc
   global fourteen_key_word_loc_c
   global fourteen_key_word_list
   global fourteen_key_word_c

   global seven_c_kw_loc
   global seven_key_word_loc
   global seven_key_word_loc_c
   global seven_key_word_list
   global seven_key_word_c

   global thirteen_c_kw_loc
   global thirteen_key_word_loc
   global thirteen_key_word_loc_c
   global thirteen_key_word_list
   global thirteen_key_word_c

   global five_key_word_list
   global five_key_word_lo
   global five_key_word_loc_c
   global five_key_word_c

   global six_c_kw_loc
   global six_key_word_loc
   global six_key_word_loc_c
   global six_key_word_list
   global six_key_word_c

   
   global eleven_c_kw_loc
   global eleven_key_word_loc
   global eleven_key_word_loc_c
   global eleven_key_word_list
   global eleven_key_word_c

   global sixteen_c_kw_loc
   global sixteen_key_word_loc
   global sixteen_key_word_loc_c
   global sixteen_key_word_list
   global sixteen_key_word_c

   global seventeen_c_kw_loc
   global seventeen_key_word_loc
   global seventeen_key_word_loc_c
   global seventeen_key_word_list
   global seventeen_key_word_c

   global eighteen_c_kw_loc
   global eighteen_key_word_loc
   global eighteen_key_word_loc_c
   global eighteen_key_word_list
   global eighteen_key_word_c

   global nineteen_c_kw_loc
   global nineteen_key_word_loc
   global nineteen_key_word_loc_c
   global nineteen_key_word_list
   global nineteen_key_word_c

   global twenty_c_kw_loc
   global twenty_key_word_loc
   global twenty_key_word_loc_c
   global twenty_key_word_list
   global twenty_key_word_c

   global twenty_one_c_kw_loc
   global twenty_one_key_word_loc
   global twenty_one_key_word_loc_c
   global twenty_one_key_word_list
   global twenty_one_key_word_c

   global twenty_tow_c_kw_loc
   global twenty_tow_key_word_loc
   global twenty_tow_key_word_loc_c
   global twenty_tow_key_word_list
   global twenty_tow_key_word_c

   global twenty_three_c_kw_loc
   global twenty_three_key_word_loc
   global twenty_three_key_word_loc_c
   global twenty_three_key_word_list
   global twenty_three_key_word_c

   global twenty_four_c_kw_loc
   global twenty_four_key_word_loc
   global twenty_four_key_word_loc_c
   global twenty_four_key_word_list
   global twenty_four_key_word_c

   global twenty_five_c_kw_loc
   global twenty_five_key_word_loc
   global twenty_five_key_word_loc_c
   global twenty_five_key_word_list
   global twenty_five_key_word_c

   
   global s_none
   global none_flag
   global n_s_del_w_loc
   global d_state_list
   
   global state_kw_list
   global state_kw_count
   global state_kw_loc
   global kw_tow_five_count
   global second_key_word_flag
   global global_obj_flag
   global global_obj_list

   global chi_flag
   global ci_flag
   global ds_flag
   global day_flag
   global open_flag
   global first_nineteen_kw_l

   global ignore_c_kw_loc
   global ignore_key_word_loc
   global ignore_key_word_loc_c
   global ignore_key_word_list
   global ignore_key_word_c
   
#-----------------------------------------------------------------------------------------
   global dy_label
   global o_label_exit_flag
   
   global first_to_five_list
   global tow_to_five_flag
   global tow_to_five_list
   global first_to_five_label
   global key_word_label

   global model_kw_label
   global ignore_kw_label
   
   global model_kw_label_flag
   global model_kw_list
   global model_kw_sum

   global model_training

   global conversion_person

   global amodel_kw_sum
   global amodel_kw_list
   global amodel_kw_label

   correct_kw_list  = 0
   temp_p_w = ''


#删除回车符号-----------replace----------------------------------------------------------------------------
   if '\n' in usr_info:
      #print('找到回车符号')

      usr_info = usr_info.strip('\n')
      storage_usr_info = usr_info
      
      #print('删除回车后字符串长度',len(usr_info))
      #os.system("pause")
#///////////////////////////////////////////////////////////////////////////////////////   
   for p_k_symbol,word in enumerate(usr_info):
       #print(word,'(%d)' % p_k_symbol)
       if word == '?' or word == '？':
             #os.system("pause")
             k_symbol_flag = True
             t_usr_in_word_len = usr_in_word_len
             usr_info = usr_info[0:t_usr_in_word_len-1]
             t_usr_in_word_len -= 1
             #print("找到特殊符号",word,'位置:',p_k_symbol,'标志位:',k_symbol_flag
                   #,'用户输入剩余长度:',t_usr_in_word_len)
             #print ('更新后的用户信息:',usr_info)
#////////////////////////////////////////////////////////////////////////////////////////
   for p_k_symbol,word in enumerate(d_person_list):#conversion_usr_info
       print(word,'(%d)' % p_k_symbol)
       if word in usr_info:
          #os.system("pause")
          global_obj_flag = True
          
          current_person_flag[current_person_flag_count] = True#注意,这里的是转换前人称
          ori_person_list[conversion_count] = word #保存原始人称(转换前)
          p_e_flag = True
          t_key_pw_loc = usr_info.find(word)
          second_person_loc = t_key_pw_loc
          person_original_loc_list[conversion_count] = second_person_loc#保存原始人称位置
          t_key_pw_len = len(word)
          
          usr_info = usr_info[0:t_key_pw_loc]+usr_info[t_key_pw_loc+t_key_pw_len:]
                    
          conversion_usr_info[conversion_count] = d_person_match[p_k_symbol]#注意
          #current_key_word = conversion_usr_info[conversion_count]
          #key_word_list[key_word_count] = current_key_word
                    
          #print('人称对象标识位状态:',current_person_flag[current_person_flag_count])          
          
          conversion_person = d_person_match[p_k_symbol]#注意

          print('对应位置翻译:',d_person_match[p_k_symbol],conversion_person)#注意
          #global_obj_list.append(conversion_person)
          #p_label = getattr(eval(conversion_person),'标签')()#获取人称标签

          #print('人称标签',p_label,model_kw_list)

          #model_kw_label_flag = True
          #model_kw_list.append(conversion_person)
          #model_kw_sum += 1
          
          print('转换中间信息人称位:',conversion_usr_info[conversion_count])#注意
          #os.system("pause")
          person_original_list[conversion_count] = word
          conversion_count += 1

          
          #key_word_count += 1
          current_person_flag_count += 1
          #print('找到关键字:',word,'起始位置:',t_key_pw_loc,'长度:',t_key_pw_len)

          info_word_st_loc[info_word_sum] = t_key_pw_loc#注意 key_word_loc
          info_word_loc_list[info_word_sum] = conversion_person
          info_word_sum += 1

          print('检测',info_word_loc_list)
          
          #print('第一次更新后的用户信息:',usr_info)
          #print('当前关键字:',current_key_word)
          #print('检查转换前人称关键字;',word)
          #print('人称关键字转换后列表内容及长度:',conversion_usr_info,conversion_count)
          #os.system("pause")
    
#继续判断是否有第二人称--------------------------------------------------------------------------------------
   for p_k_symbol,word in enumerate(d_sperson_list):#conversion_usr_info
       #print(word,'(%d)' % p_k_symbol)
       if word in usr_info:#or'你是'or'你想'or'你要':#后续人称关键字分支代码需补充
          #os.system("pause")   
          current_person_flag[current_person_flag_count] = True#注意,这里的是转换前人称
          ori_person_list[conversion_count] = word#保存原始人称(转换前)
          p_e_flag = True
          global_obj_flag = True
          
          t_key_pw_loc = usr_info.find(word)
          first_person_loc = t_key_pw_loc
          person_original_loc_list[conversion_count] = first_person_loc#保存原始人称位置
          t_key_pw_len = len(word)
          
          usr_info = usr_info[0:t_key_pw_loc]+usr_info[t_key_pw_loc+t_key_pw_len:]
                    
          conversion_usr_info[conversion_count] = d_sperson_match[p_k_symbol]#注意
          #current_key_word = conversion_usr_info[conversion_count]
          #key_word_list[key_word_count] = current_key_word
                    
          #print('人称对象标识位状态:',current_person_flag[current_person_flag_count])
          
          
          conversion_person = d_sperson_match[p_k_symbol]

          print('对应位置翻译:',d_sperson_match[p_k_symbol],conversion_person)#注意
          #global_obj_list.append(conversion_person)
          #sp_label = getattr(eval(conversion_person),'标签')()#获取人称标签
          #print('人称标签',sp_label)
          
          conversion_person_key_word = d_sperson_match[p_k_symbol]#注意

          #model_kw_label_flag = True
          #model_kw_list.append(conversion_person)
          #model_kw_sum += 1
                  
          #print('转换中间信息人称位:',conversion_usr_info[conversion_count])#注意
          #os.system("pause")
          person_original_list[conversion_count] = word
          conversion_count += 1 
          if conversion_count > 1:#判断是否有第二个人称字符出现
             s_p_exist_flag = True
             #os.system("pause")
          #key_word_count += 1
          current_person_flag_count += 1
          #print('找到关键字:',word,'起始位置:',t_key_pw_loc,'长度:',t_key_pw_len)
          
          info_word_st_loc[info_word_sum] = t_key_pw_loc#注意 key_word_loc
          info_word_loc_list[info_word_sum] = conversion_person
          info_word_sum += 1
          
          #print('更新后的用户信息-person:',usr_info)
          #print('当前关键字:',current_key_word)
          #print('检查转换前人称关键字;',word)
          #print('人称关键字转换后列表内容及长度:',conversion_usr_info,conversion_count)
          #print('原始人称列表及位置',person_original_list,person_original_loc_list)
          if s_p_exist_flag == True:#判断第一及第二人称转换后位置是否正确
             if person_original_loc_list[0] > person_original_loc_list[1]:
                temp_p_w = conversion_usr_info[1]
                conversion_usr_info[1] = conversion_usr_info[0]
                conversion_usr_info[0] = temp_p_w
                #print('交换人称位置后的转换列表',conversion_usr_info)
          #os.system("pause")    
#///////////////////////////////////////////////////////////////////////////////////////////////////////////          
          
   if (k_symbol_flag == False) and (p_e_flag == False):#(word not in storage_usr_info):
         n_ksym_kperson = True
         #print('关键符号及人称都不存在',n_ksym_kperson,p_e_flag,k_symbol_flag)
   #print(k_symbol_flag,p_e_flag)
   #os.system("pause")  
#///////////////////////////////////////////////////////////////////////////////////////           
   
   print("*********************************************************************************")      
#///////////////////////////////////////////////////////////////////////////////////////////////////
   #if p_kw_special_l_loc == False:#检测连接特殊位置状态是否有效
   for c,d in enumerate(d_state_list):

          #print('状态及连接字符列表内容:',c,d)
          for key,value in d.items():
              #print('键:',key,"值:",value)
              
#///////////////////////////////////////////////////////////////////////////////////////////////////                  
              if key in usr_info:#注意
                print(key)
                #os.system("pause")global ignore_loc_c_kw_loc

                 
                if (key == '的' or key == '请问' or key == '很' or  key == '吗' or key == '了'
                    or key == '那么' or key == '这么' or key == '难道' or key == '非常'
                    or key == '得' or key == '暂时' or key == '些'
                    or key == '以及' or key == '里' or key == '帮忙' or key == '帮助'
                    or key == '协助' or key == '把' #or key == '和'
                    or key == '说说' or key == '这样' or key == '那样'):
                      
                    value  = True
                    d[key] = True
                    #info_word_sum += 1#注意
                    
                    ignore_key_word_loc[ignore_key_word_loc_c] = storage_usr_info.find(key)
                    ignore_key_word_loc_c += 1
                    ignore_key_word_list[ignore_key_word_c] = key
                    ignore_key_word_c += 1


                    print(key)

                    print(usr_info)                    
                    #os.system("pause")
#--------------------------------------------------------------------------------------------------   
#--------------------------------------------------------------------------------------------------
                 
                elif (key == '哪个' or key == '哪一个' or key == '谁'): 
                     value =  True
                     d[key] = True
                     
                     eleven_key_word_loc[eleven_key_word_loc_c] = storage_usr_info.find(key)
                     eleven_key_word_loc_c += 1
                     eleven_key_word_list[eleven_key_word_c] = key
                     eleven_key_word_c += 1

                     key_word_list_content[key_word_list_content_c] = key
                     key_word_list_content_flag[key_word_list_content_c] = True#注意
                     key_word_list_content_c += 1

                     model_kw_label_flag = True
                     model_kw_list.append(key)
                     model_kw_sum += 1

                     eleven_kw_flag = True
                     o_label_exit_flag = True
                     all_kw_flag_list[10] = True        
                    #os.system("pause")                    
#r--------------------------------------------------------------------------------------------------

                elif (key == '没有'  or key == '有没有' or key ==  '有' or key == '没'): 
                     value =  True
                     d[key] = True
                     
                     eleven_key_word_loc[eleven_key_word_loc_c] = storage_usr_info.find(key)
                     eleven_key_word_loc_c += 1
                     eleven_key_word_list[eleven_key_word_c] = key
                     eleven_key_word_c += 1

                     key_word_list_content[key_word_list_content_c] = key
                     key_word_list_content_flag[key_word_list_content_c] = True#注意
                     key_word_list_content_c += 1

                     model_kw_label_flag = True
                     model_kw_list.append(key)
                     model_kw_sum += 1

                     eleven_kw_flag = True
                     o_label_exit_flag = True
                     all_kw_flag_list[10] = True        
                    #os.system("pause")
#--------------------------------------------------------------------------------------------------
                elif (key == '失去' or key == '丢失' or key == '遗失' or key == '弄丢'
                      or key == '消失' or key == '丢弃'): 
                     value =  True
                     d[key] = True
                     
                     eleven_key_word_loc[eleven_key_word_loc_c] = storage_usr_info.find(key)
                     eleven_key_word_loc_c += 1
                     eleven_key_word_list[eleven_key_word_c] = key
                     eleven_key_word_c += 1

                     key_word_list_content[key_word_list_content_c] = key
                     key_word_list_content_flag[key_word_list_content_c] = True#注意
                     key_word_list_content_c += 1

                     model_kw_label_flag = True
                     model_kw_list.append(key)
                     model_kw_sum += 1

                     eleven_kw_flag = True
                     o_label_exit_flag = True
                     all_kw_flag_list[10] = True        
                    #os.system("pause")
#--------------------------------------------------------------------------------------------------
                elif ( key == '差'
                      or key == '不存在' or key == '放弃' or key == '不见' or key == '生存'
                      or key == '糟糕'  or key == '好'or key == '不好' or key == '不在'
                      or key == '差劲' or key == '失败'  or key == '优秀'                    
                      or key =='占有' or key == '在' or key == '不错'
                      or key == '出现' or key == '存在' or key == '良好' or key == '优秀'
                      or key == '出众' or key == '优良' or key == '很好' or key == '非常好'
                      or key == '胜利' or key == '出色' or key == '赢'or key == '输'):
                    value  = True
                    d[key] = True
    

                    five_key_word_loc[five_key_word_loc_c] = storage_usr_info.find(key)
                    five_key_word_loc_c += 1
                    five_key_word_list[five_key_word_c] = key
                    five_key_word_c += 1
                    
                    five_kw_flag = True

                    #ll_kw_flag_list[4] = True

                    #key_word_list_content[key_word_list_content_c] = key
                    #key_word_list_content_flag[key_word_list_content_c] = True#注意
                    #key_word_list_content_c += 1
                    #global_obj_flag = True
                    smodel_kw_label_flag = True
                    smodel_kw_list.append(key)
                    smodel_kw_sum += 1
                     
                    #c_kw_flag = value#注意
                    #current_state_flag[0] = c_kw_flag

                    all_kw_flag_list[4] = True

                     
                    print(value,d[key],key)
                    #os.system("pause")
#--------------------------------------------------------------------------------------------------
                elif (key == '说' or key == '讲'):

                     value =  True
                     d[key] = True
                     

                     key_word_list_content[key_word_list_content_c] = key
                     key_word_list_content_flag[key_word_list_content_c] = True#注意
                     key_word_list_content_c += 1

                     tow_to_five_flag = True
                     tow_to_five_list.append(key)
                     model_kw_sum += 1

                     nine_kw_flag = True
                     o_label_exit_flag = True
                     all_kw_flag_list[8] = True
#--------------------------------------------------------------------------------------------------
                elif (key == '打开' or key == '开' or key == '拿给' or key == '给'):

                     value =  True
                     d[key] = True
                     

                     key_word_list_content[key_word_list_content_c] = key
                     key_word_list_content_flag[key_word_list_content_c] = True#注意
                     key_word_list_content_c += 1

                     tow_to_five_flag = True
                     tow_to_five_list.append(key)
                     model_kw_sum += 1

                     nine_kw_flag = True
                     o_label_exit_flag = True
                     all_kw_flag_list[8] = True 
#--------------------------------------------------------------------------------------------------
                elif (key == '考试' or key == '考核'or key == '测试' or key == '检测'
                      or key == '检查' or key == '考' or key == '唱歌'
                      or key == '唱'or key == '跳舞' or key == '跳' 
                      or key == '玩' or key == '买'
                      or key == '打' or key == '拿' or key == '走'  or key == '吃'
                      or key == '吵架' or key == '思考' or key == '猜测' or key == '想想'
                      or key == '感觉' or key == '睡眠' or key == '创造' or key == '设计'
                      or key == '制造' or key == '生产' or key == '在干嘛' or key == '在干什么'
                      or key == '交给' or key == '哈哈大笑'  or key == '大笑' or key == '笑'):
                     value  = True
                     d[key] = True
                     #info_word_sum += 1#注意
                     
                     second_key_word_loc[second_key_word_loc_c] = storage_usr_info.find(key)
                     second_key_word_loc_c += 1
                     second_key_word_list[second_key_word_c] = key
                     second_key_word_c += 1

                     #kw_tow_five_count += 1
                     #kw_tow_five_list[0] = key
                     all_kw_flag_list[1] = True

                     tow_to_five_flag = True
                     tow_to_five_list.append(key)
                     model_kw_sum += 1

                     #tow_to_five_flag.append(all_kw_flag_list[1])
                     #tow_to_five_list.append(key)

                     #key_word_list_content[key_word_list_content_c] = key
                     #key_word_list_content_flag[key_word_list_content_c] = True#注意
                     #key_word_list_content_c += 1
                    
                     #c_kw_flag = value#注意
                     #current_state_flag[0] = c_kw_flag
                     second_kw_flag = True
                     print(key,key_word_list_content,second_key_word_list,second_key_word_c)
                     #os.system("pause")
#--------------------------------------------------------------------------------------------------
                elif (key == '数量'  or key == '非常快' or key == '太快' or key == '很快'                      or key == '几' or key == '一天' or key == '每天'
                      or key == '多' or key == '非常少' or key == '很少' or key == '非常快'
                      or key == '更少' or key == '更多' or key == '比较少' or key == '太快' or key == '很快'
                      or key == '更快' or key == '比较多' or key == '足够' or key == '充足'
                      or key == '够'   or key == '概率' or key == '身高' or key == '可能性'
                      or key == '体重'):

                     value =  True
                     d[key] = True
                     
                     eight_key_word_loc[eight_key_word_loc_c] = storage_usr_info.find(key)
                     eight_key_word_loc_c += 1
                     eight_key_word_list[eight_key_word_c] = key
                     eight_key_word_c += 1

                     smodel_kw_label_flag = True
                     smodel_kw_list.append(key)
                     smodel_kw_sum += 1

                     key_word_list_content[key_word_list_content_c] = key
                     key_word_list_content_flag[key_word_list_content_c] = True#注意
                     key_word_list_content_c += 1

                     eight_kw_flag = True
                     o_label_exit_flag = True
                     all_kw_flag_list[7] = True
#---------------------------------------------------------------------------------------------------
                elif (key == '心情' or key == '情绪'):

                     value =  True
                     d[key] = True
                     
                     nine_key_word_loc[nine_key_word_loc_c] = storage_usr_info.find(key)
                     nine_key_word_loc_c += 1
                     nine_key_word_list[eight_key_word_c] = key
                     nine_key_word_c += 1

                     key_word_list_content[key_word_list_content_c] = key
                     key_word_list_content_flag[key_word_list_content_c] = True#注意
                     key_word_list_content_c += 1

                     tow_to_five_flag = True
                     tow_to_five_list.append(key)
                     model_kw_sum += 1

                     nine_kw_flag = True
                     o_label_exit_flag = True
                     all_kw_flag_list[8] = True    
#---------------------------------------------------------------------------------------------------
                elif (key == '比'):

                     value =  True
                     d[key] = True
                     
                     nine_key_word_loc[nine_key_word_loc_c] = storage_usr_info.find(key)
                     nine_key_word_loc_c += 1
                     nine_key_word_list[eight_key_word_c] = key
                     nine_key_word_c += 1

                     key_word_list_content[key_word_list_content_c] = key
                     key_word_list_content_flag[key_word_list_content_c] = True#注意
                     key_word_list_content_c += 1

                     model_kw_label_flag = True
                     model_kw_list.append(key)
                     model_kw_sum += 1

                     nine_kw_flag = True
                     o_label_exit_flag = True
                     all_kw_flag_list[8] = True
#---------------------------------------------------------------------------------------------------
                elif (key == '依靠' or key == '依赖'):

                     value =  True
                     d[key] = True
                     
                     nine_key_word_loc[nine_key_word_loc_c] = storage_usr_info.find(key)
                     nine_key_word_loc_c += 1
                     nine_key_word_list[eight_key_word_c] = key
                     nine_key_word_c += 1

                     key_word_list_content[key_word_list_content_c] = key
                     key_word_list_content_flag[key_word_list_content_c] = True#注意
                     key_word_list_content_c += 1

                     tow_to_five_flag = True
                     tow_to_five_list.append(key)
                     model_kw_sum += 1

                     nine_kw_flag = True
                     o_label_exit_flag = True
                     all_kw_flag_list[8] = True     
#---------------------------------------------------------------------------------------------------

                elif (key == '大' or key == '小'):

                     value =  True
                     d[key] = True
                     
                     ten_key_word_loc[ten_key_word_loc_c] = storage_usr_info.find(key)
                     ten_key_word_loc_c += 1
                     ten_key_word_list[eight_key_word_c] = key
                     ten_key_word_c += 1

                     key_word_list_content[key_word_list_content_c] = key
                     key_word_list_content_flag[key_word_list_content_c] = True#注意
                     key_word_list_content_c += 1

                     smodel_kw_label_flag = True
                     smodel_kw_list.append(key)
                     smodel_kw_sum += 1

                     ten_kw_flag = True
                     o_label_exit_flag = True
                     all_kw_flag_list[9] = True        
#---------------------------------------------------------------------------------------------------                     
                elif ( key == '只' or key == '双' or key == '个'
                       or key == '单' or key == '栋' or key == '间'
                       or key == '部'or key == '辆' or key == '艘'or key == '架'
                       or key == '台'or  key == '顿'
                       or key == '次' ):
 
                     value =  True
                     d[key] = True
                     #info_word_sum += 1#注意                                         
                     #nus_loc_key_word_loc[nus_loc_key_word_loc_c] = storage_usr_info.find(key)

                     #nus_loc_key_word_loc_c += 1
                     #nus_loc_key_word_list[nus_loc_key_word_c] = key
                     #nus_loc_key_word_c += 1
                    
                     #c_kw_flag = value#注意
                     #current_state_flag[0] = c_kw_flag
                     #loc_flag = True
                     #nus_loc_flag = True
                     o_label_exit_flag = True
                     #global_obj_flag = True

                     fourteen_key_word_loc[fourteen_key_word_loc_c] = storage_usr_info.find(key)
                     fourteen_key_word_loc_c += 1
                     fourteen_key_word_list[fourteen_key_word_c] = key
                     fourteen_key_word_c += 1

                     key_word_list_content[key_word_list_content_c] = key
                     key_word_list_content_flag[key_word_list_content_c] = True #注意
                     key_word_list_content_c += 1

                     #kw_tow_five_count += 1
                     #kw_tow_five_list[14] =key
                     all_kw_flag_list[13] = True
                    
                     #c_kw_flag = value#注意
                     #current_state_flag[0] = c_kw_flag
                     fourteen_kw_flag = True
                     #print(key)
                     #os.system("pause")
#----------------------------------------------------------------------------------------------------
                elif (key == '0' or key == '1' or key == '2'
                      or key == '3' or key == '4' or key == '5'
                      or key == '6' or key == '7' or key == '8'
                      or key == '9' or key == '一' or key == '二'
                      or key == '三' or key == '四' or key == '五'
                      or key == '六' or key == '七' or key == '八'
                      or key == '九' or key == '零'or key == '十'):

                     value =  True
                     d[key] = True
                     all_kw_flag_list[14] = True
                  
                     o_label_exit_flag = True#注意
                     key_word_list_content[key_word_list_content_c] = key#注意                     
                     key_word_list_content_flag[key_word_list_content_c] = True#注意
                     key_word_list_content_c += 1#注意

                     fifteen_key_word_loc[fifteen_key_word_loc_c] = storage_usr_info.find(key)
                     fifteen_key_word_loc_c += 1
                     fifteen_key_word_list[fifteen_key_word_c] = key
                     fifteen_key_word_c += 1

                     #c_kw_flag = value#注意
                     #current_state_flag[0] = c_kw_flag
                     fifteen_kw_flag = True
#----------------------------------------------------------------------------------------------------                     
                elif (key == '现在'):

                  value =  True 
                  d[key] = True
                  #info_word_sum += 1#注意    

                  #kw_tow_five_list[15] = key
                  all_kw_flag_list[21] = True
                  
                  #o_label_exit_flag = True
                  key_word_list_content[key_word_list_content_c] = key#注意                     
                  key_word_list_content_flag[key_word_list_content_c] = True#注意
                  key_word_list_content_c += 1#注意

                  twenty_four_key_word_loc[twenty_four_key_word_loc_c] = storage_usr_info.find(key)
                  twenty_four_key_word_loc_c += 1
                  twenty_four_key_word_list[twenty_four_key_word_c] = key
                  twenty_four_key_word_c += 1

                  #smodel_kw_label_flag = True
                  #smodel_kw_list.append(key)
                  #smodel_kw_sum += 1

                  #c_kw_flag = value#注意
                  #current_state_flag[0] = c_kw_flag
                  twenty_four_kw_flag = True
                  #print(model_kw_list)
                  #os.system("pause")  
#--------------------------------------------------------------------------------------------------- 

#----------------------------------------------------------------------------------------------------                     

                elif (key == '过去' or key == '这里' or key == '从哪里' or key == '过来'
                      or key == '哪里' or key == '那里' or key == '这儿'
                      or key == '那里' or key =='在哪' or key =='地方' or key == '离开'
                      or key == '走开' or key == '过去' or key == '过来' or key == '去'
                      or key == '住在' or key == '在' or key == '来'):
 
                     value =  True
                     d[key] = True
                     #info_word_sum += 1#注意                     
                     #se_loc_key_word_loc[se_loc_key_word_loc_c] = storage_usr_info.find(key)
                     #se_loc_key_word_loc_c += 1
                     #se_loc_key_word_list[se_loc_key_word_c] = key
                     #se_loc_key_word_c += 1
                    
                     #c_kw_flag = value#注意 thirteen
                     #current_state_flag[0] = c_kw_flag
                     loc_flag = True
                     se_loc_flag = True

                     tow_to_five_flag = True
                     tow_to_five_list.append(key)
                     #model_kw_sum += 1

                     thirteen_key_word_loc[twelve_key_word_loc_c] = storage_usr_info.find(key)
                     thirteen_key_word_loc_c += 1
                     thirteen_key_word_list[thirteen_key_word_c] = key
                     thirteen_key_word_c += 1

                     key_word_list_content[key_word_list_content_c] = key
                     key_word_list_content_flag[key_word_list_content_c] = True#注意
                     key_word_list_content_c += 1

                     #kw_tow_five_count += 1 thirteen_c_kw_loc = 0 
                                          
                     #kw_tow_five_list[12] =key
                     all_kw_flag_list[13] = True

                     #c_kw_flag = value#注意
                     #current_state_flag[0] = c_kw_flag
                     thirteen_kw_flag = True

#---------------------------------------------------------------------------------------------------
                elif (key == '疲惫'
                      or key == '高兴' or key == '开心' or key == '郁闷' or key == '难过'
                      or key == '损坏' or key == '损失' or key == '损伤' or key == '良好'
                      or key == '兴奋' or key == '受伤' or key == '伤' or key == '流血'
                      or key == '骨折' or key == '扭伤' or key == '幸福' or key == '健康'
                      or key == '勤奋' or key == '努力' or key == '勤劳' or key == '和平'):
                     value  = True
                     d[key] = True

                     four_key_word_loc[four_key_word_loc_c] = storage_usr_info.find(key)
                     four_key_word_loc_c += 1
                     four_key_word_list[four_key_word_c] = key
                     four_key_word_c += 1
                     four_kw_flag = True
                     #global_obj_flag = True

                     all_kw_flag_list[3] = True

                     tow_to_five_flag = True
                     tow_to_five_list.append(key)
                     model_kw_sum += 1


                     #key_word_list_content[key_word_list_content_c] = key#注意                     
                     #key_word_list_content_flag[key_word_list_content_c] = True#注意
                     #key_word_list_content_c += 1#注意
                    
                     #c_kw_flag = value#注意
                     #current_state_flag[0] = c_kw_flag
                     print(key,four_key_word_list,four_key_word_c)
                     #os.system("pause")
#---------------------------------------------------------------------------------------------------
                elif (key == '摔' or key == '翻倒' or key == '翻'):
                     value  = True
                     d[key] = True

                     three_key_word_loc[three_key_word_loc_c] = storage_usr_info.find(key)
                     three_key_word_loc_c += 1
                     three_key_word_list[three_key_word_c] = key
                     three_key_word_c += 1
                     three_kw_flag = True
                     #global_obj_flag = True
                     all_kw_flag_list[3] = True
                     
                     tow_to_five_flag.append(all_kw_flag_list[2])
                     tow_to_five_list.append(key)

                     #key_word_list_content[key_word_list_content_c] = key#注意                     
                     #key_word_list_content_flag[key_word_list_content_c] = True#注意
                     #key_word_list_content_c += 1#注意
                    
                     #c_kw_flag = value#注意
                     #current_state_flag[0] = c_kw_flag
                     print(key,three_key_word_list,three_key_word_c)
#---------------------------------------------------------------------------------------------------
                elif (key == '文化' or key == '文字' or key == '饮食' or key == '时尚'
                      or key == '生活' or key == '故事' or key == '笑话'                   
                      or key == '习惯' or key == '代码' or key == '编码'):
                      
                     value  = True
                     d[key] = True

                     six_key_word_loc[six_key_word_loc_c] = storage_usr_info.find(key)
                     six_key_word_loc_c += 1
                     six_key_word_list[six_key_word_c] = key
                     six_key_word_c += 1
                     six_kw_flag = True

                     all_kw_flag_list[5] = True
                     #global_obj_flag = True
                     #tow_to_five_flag.append(all_kw_flag_list[5])
                     #tow_to_five_list.append(key)

                     #tow_to_five_label

                     smodel_kw_label_flag = True
                     smodel_kw_list.append(key)
                     smodel_kw_sum += 1

                     #key_word_list_content[key_word_list_content_c] = key#注意                     
                     #key_word_list_content_flag[key_word_list_content_c] = True#注意
                     #key_word_list_content_c += 1#注意
                    
                     #c_kw_flag = value#注意
                     #current_state_flag[0] = c_kw_flag
                     print(key,six_key_word_list,six_key_word_c)
                     #os.system("pause")           
#---------------------------------------------------------------------------------------------------
                elif ( key == '沟通' or key == '交流' or key == '交往'):
                      
                     value  = True
                     d[key] = True

                     smodel_kw_label_flag = True
                     smodel_kw_list.append(key)
                     smodel_kw_sum += 1
                     
                     print(key,six_key_word_list,six_key_word_c)
                     #os.system("pause")          
#-----------------------------------------------------------------------------------------------------
                elif ( key == '使用' or key == '用' or key == '利用'):
                      
                     value  = True
                     d[key] = True

                     smodel_kw_label_flag = True
                     smodel_kw_list.append(key)
                     smodel_kw_sum += 1
                     
                     print(key,six_key_word_list,six_key_word_c)
                     #os.system("pause")
#---------------------------------------------------------------------------------------------------
                elif (key == '和'):                      
                     value  = True
                     d[key] = True                    

                     tow_to_five_flag = True
                     tow_to_five_list.append(key)
                     model_kw_sum += 1
                     #os.system("pause")                
#-----------------------------------------------------------------------------------------------------
                elif (key == '只能' or key == '只会' or key == '只可以'):

                  value =  True 
                  d[key] = True
                  #info_word_sum += 1#注意    

                  #kw_tow_five_list[15] = key
                  all_kw_flag_list[21] = True
                  
                  #o_label_exit_flag = True
                  key_word_list_content[key_word_list_content_c] = key#注意                     
                  key_word_list_content_flag[key_word_list_content_c] = True#注意
                  key_word_list_content_c += 1#注意

                  twenty_five_key_word_loc[twenty_five_key_word_loc_c] = storage_usr_info.find(key)
                  twenty_five_key_word_loc_c += 1
                  twenty_five_key_word_list[twenty_five_key_word_c] = key
                  twenty_five_key_word_c += 1

                  smodel_kw_label_flag = True
                  smodel_kw_list.append(key)
                  smodel_kw_sum += 1

                  #c_kw_flag = value#注意
                  #current_state_flag[0] = c_kw_flag
                  twenty_five_kw_flag = True
                  #print(model_kw_list)
                  #os.system("pause")
#---------------------------------------------------------------------------------------------------
                elif (key == '准备' or key == '即将' or key == '马上' or key == '想'
                      or key == '立即' or key == '尽快' or key == '快了' or key == '努力'
                      or key == '争取' or key == '尽可能' or key == '尽量' or key == '一定'
                      or key == '会做' or key == '能做' or key == '懂做'
                      or key == '技术' or key == '技能'
                      or key == '能'   or key == '会' or key == '可以' 
                      or key == '必需' or key == '必须' or key == '答应' or key == '允许'
                      or key == '危险' or key == '需要' or key == '必须'
                      or key == '除非' or key == '计划' or key == '即刻'
                      or key == '立刻' or key == '以后' or key == '将来' or key == '未来'
                      or key == '马上'):
                     value =  True
                     d[key] = True
                     #info_word_sum += 1#注意
                     
                     #ftime_key_word_loc[ftime_key_word_loc_c] = storage_usr_info.find(key)
                     #ftime_key_word_loc_c += 1
                     #ftime_key_word_list[ftime_key_word_c] = key
                     #ftime_key_word_c += 1#eight


                     twelve_key_word_loc[twelve_key_word_loc_c] = storage_usr_info.find(key)
                     twelve_key_word_loc_c += 1
                     twelve_key_word_list[twelve_key_word_c] = key
                     twelve_key_word_c += 1
                     
                     model_kw_label_flag = True
                     model_kw_list.append(key)
                     model_kw_sum += 1
                     #ignore_kw_label = []
                     #kw_tow_five_list[11] =key
                     all_kw_flag_list[11] = True
                     
                     #o_label_exit_flag = True
                     
                     key_word_list_content[key_word_list_content_c] = key#注意                     
                     key_word_list_content_flag[key_word_list_content_c] = True#注意
                     key_word_list_content_c += 1#注意
                     
                     #c_kw_flag = value#注意
                     #current_state_flag[0] = c_kw_flag
                     ftime_flag = True
                     a_f_sd_flag = True
                     twelve_kw_flag = True
                     #print(usr_info,key,ftime_key_word_list)
                     #os.system("pause")
#---------------------------------------------------------------------------------------------------
                                     
#---------------------------------------------------------------------------------------------------                               
                elif (key == '为什么'  or  key == '就应该' or key == '为何' or key == '为啥'
                      or key == '什么' or  key == '应当'  or key == '时候' or key == '时'
                      or key == '怎么了' or key == '如何' or key == '才可以' or key == '怎样'
                      or key == '怎么办' or key == '怎样' or key == '才能' 
                      or key == '怎么样' or key == '怎么' or key == '如果'
                      or key == '就' or key == '就要'
                      or key == '就会' or key == '因为' or key == '所以' or key == '应该'
                      or key == '原因'):

                  value =  True
                  d[key] = True
                  #info_word_sum += 1#注意    

                  #kw_tow_five_list[15] = key
                  all_kw_flag_list[16] = True
                  
                  #o_label_exit_flag = True
                  key_word_list_content[key_word_list_content_c] = key#注意                     
                  key_word_list_content_flag[key_word_list_content_c] = True#注意
                  key_word_list_content_c += 1#注意

                  seventeen_key_word_loc[seventeen_key_word_loc_c] = storage_usr_info.find(key)
                  seventeen_key_word_loc_c += 1
                  seventeen_key_word_list[seventeen_key_word_c] = key
                  seventeen_key_word_c += 1

                  model_kw_label_flag = True
                  model_kw_list.append(key)
                  model_kw_sum += 1

                  #c_kw_flag = value#注意
                  #current_state_flag[0] = c_kw_flag
                  seventeen_kw_flag = True
                  #ftime_flag  = True
                  #a_f_sd_flag = True
                  #os.system("pause")
#---------------------------------------------------------------------------------------------------
                #eighteen
                elif (key == '使命' or key == '目标' or key == '意义'
                      or key == '维持' or key == '维护' or key == '保持'):

                  value =  True
                  d[key] = True
                  #info_word_sum += 1#注意    

                  #kw_tow_five_list[15] = key
                  all_kw_flag_list[17] = True
                  
                  o_label_exit_flag = True
                  key_word_list_content[key_word_list_content_c] = key#注意                     
                  key_word_list_content_flag[key_word_list_content_c] = True#注意
                  key_word_list_content_c += 1#注意

                  eighteen_key_word_loc[eighteen_key_word_loc_c] = storage_usr_info.find(key)
                  eighteen_key_word_loc_c += 1
                  eighteen_key_word_list[eighteen_key_word_c] = key
                  eighteen_key_word_c += 1

                  tow_to_five_flag = True
                  tow_to_five_list.append(key)
                  model_kw_sum += 1

                  #c_kw_flag = value#注意
                  #current_state_flag[0] = c_kw_flag
                  eighteen_kw_flag = True
                  #ftime_flag  = True
                  #a_f_sd_flag = True nineteen
#---------------------------------------------------------------------------------------------------
                elif (key == '过程' or key == '结果' or key == '后果'
                      or key == '结局' or key == '下场' or key == '开始'
                      or key == '开头' or key == '终止' or key == '中止'):

                  value =  True
                  d[key] = True
                  #info_word_sum += 1#注意    

                  #kw_tow_five_list[15] = key
                  all_kw_flag_list[16] = True
                  #global_obj_flag = True
                  #o_label_exit_flag = True
                  key_word_list_content[key_word_list_content_c] = key#注意                     
                  key_word_list_content_flag[key_word_list_content_c] = True#注意
                  key_word_list_content_c += 1#注意

                  nineteen_key_word_loc[nineteen_key_word_loc_c] = storage_usr_info.find(key)
                  nineteen_key_word_loc_c += 1
                  nineteen_key_word_list[nineteen_key_word_c] = key
                  nineteen_key_word_c += 1

                  smodel_kw_label_flag = True
                  smodel_kw_list.append(key)
                  smodel_kw_sum += 1

                  #c_kw_flag = value#注意
                  #current_state_flag[0] = c_kw_flag
                  nineteen_kw_flag = True  
#------------------------------------------------------------------------------------------------------
                elif (key == '获得' or key == '收获' or key == '得到' or key == '获得'
                      or key == '获取' or key == '拥有'  or key == '取得'
                      or key == '占用' or key == '叫'  or key == '无法'):

                  value =  True 
                  d[key] = True
                  #info_word_sum += 1#注意    

                  #kw_tow_five_list[15] = key
                  all_kw_flag_list[19] = True
                  
                  #o_label_exit_flag = True
                  key_word_list_content[key_word_list_content_c] = key#注意                     
                  key_word_list_content_flag[key_word_list_content_c] = True#注意
                  key_word_list_content_c += 1#注意

                  twenty_key_word_loc[twenty_key_word_loc_c] = storage_usr_info.find(key)
                  twenty_key_word_loc_c += 1
                  twenty_key_word_list[twenty_key_word_c] = key
                  twenty_key_word_c += 1

                  tow_to_five_flag = True
                  tow_to_five_list.append(key)
                  model_kw_sum += 1

                  #c_kw_flag = value#注意
                  #current_state_flag[0] = c_kw_flag
                  twenty_kw_flag = True
                  #os.system("pause")
#------------------------------------------------------------------------------------------------------
                elif (key == '可能' or key == '也行' or key == '可能吗'
                      or key == '能不能' or key == '可不可以' or key == '行不行'
                      or key == '会不会' or key == '好吗'or key == '行吗'
                      or key == '可以吗'):

                  value =  True 
                  d[key] = True
                  #info_word_sum += 1#注意    

                  #kw_tow_five_list[15] = key
                  all_kw_flag_list[20] = True
                  
                  #o_label_exit_flag = True
                  key_word_list_content[key_word_list_content_c] = key#注意                     
                  key_word_list_content_flag[key_word_list_content_c] = True#注意
                  key_word_list_content_c += 1#注意

                  twenty_one_key_word_loc[twenty_one_key_word_loc_c] = storage_usr_info.find(key)
                  twenty_one_key_word_loc_c += 1
                  twenty_one_key_word_list[twenty_one_key_word_c] = key
                  twenty_one_key_word_c += 1

                  model_kw_label_flag = True
                  model_kw_list.append(key)
                  model_kw_sum += 1

                  #c_kw_flag = value#注意
                  #current_state_flag[0] = c_kw_flag
                  twenty_one_kw_flag = True
#---------------------------------------------------------------------------------------------------
                elif (key == '名字' or key == '姓名' or key == '小名' or
                      key == '称呼' or key == '外号' or key == '英文名'):

                  value =  True 
                  d[key] = True
                  #info_word_sum += 1#注意    

                  #kw_tow_five_list[15] = key
                  all_kw_flag_list[21] = True
                  #global_obj_flag = True
                  #o_label_exit_flag = True
                  key_word_list_content[key_word_list_content_c] = key#注意                     
                  key_word_list_content_flag[key_word_list_content_c] = True#注意
                  key_word_list_content_c += 1#注意

                  twenty_tow_key_word_loc[twenty_tow_key_word_loc_c] = storage_usr_info.find(key)
                  twenty_tow_key_word_loc_c += 1
                  twenty_tow_key_word_list[twenty_tow_key_word_c] = key
                  twenty_tow_key_word_c += 1

                  smodel_kw_label_flag = True
                  smodel_kw_list.append(key)
                  smodel_kw_sum += 1

                  #c_kw_flag = value#注意
                  #current_state_flag[0] = c_kw_flag
                  twenty_tow_kw_flag = True
                  #print(model_kw_list)
                  #os.system("pause")
#----------------------------------------------------------------------------------------------------
                elif (key == '是' or key == '不是' or key == '还是' or key == '是不是'
                      or key == '不能' or key == '不会' or key == '不行' or key == '不可以'
                      or key == '不可能' or key == '一定' or key == '否则'
                      or key == '不然' or key == '要不'):

                  value =  True 
                  d[key] = True
                  #info_word_sum += 1#注意    

                  #kw_tow_five_list[15] = key
                  all_kw_flag_list[21] = True
                  
                  #o_label_exit_flag = True
                  key_word_list_content[key_word_list_content_c] = key#注意                     
                  key_word_list_content_flag[key_word_list_content_c] = True#注意
                  key_word_list_content_c += 1#注意

                  twenty_three_key_word_loc[twenty_three_key_word_loc_c] = storage_usr_info.find(key)
                  twenty_three_key_word_loc_c += 1
                  twenty_three_key_word_list[twenty_three_key_word_c] = key
                  twenty_three_key_word_c += 1

                  model_kw_label_flag = True
                  model_kw_list.append(key)
                  model_kw_sum += 1

                  #c_kw_flag = value#注意
                  #current_state_flag[0] = c_kw_flag
                  twenty_three_kw_flag = True
                  #print(model_kw_list)
                  #os.system("pause")  
#----------------------------------------------------------------------------------------------------
                elif (key == '相同' or key == '相似'or key == '类似' or key == '一样'
                  or key == '一致' or key == '差别' or key == '区别'):
                  value  = True
                  d[key] = True
                  #info_word_sum += 1#注意 twenty
                     
                  sixteen_key_word_loc[sixteen_key_word_loc_c] = storage_usr_info.find(key)
                  sixteen_key_word_loc_c += 1
                  sixteen_key_word_list[fourteen_key_word_c] = key
                  sixteen_key_word_c += 1

                  #kw_tow_five_count += 1
                  #kw_tow_five_list[14] = key
                  all_kw_flag_list[16] = True
                  o_label_exit_flag = True

                  model_kw_label_flag = True
                  model_kw_list.append(key)
                  model_kw_sum += 1

                  key_word_list_content[key_word_list_content_c] = key#注意                     
                  key_word_list_content_flag[key_word_list_content_c] = True#注意
                  key_word_list_content_c += 1#注意
                    
                  #c_kw_flag = value#注意
                  #current_state_flag[0] = c_kw_flag
                  sixteen_kw_flag = True
                  #print(model_kw_list)
                  #os.system("pause")                
#---------------------------------------------------------------------------------------------------                  
#----------------------------------------------------------------------------------------------------                
#----------------------------------------------------------------------------------------------------                    
                else:       
                     d[key] = True
                     value  = True
                     #info_word_sum += 1#注意
                     #print('用户信息:',usr_info,'键:',key,'值:',value)
                     #os.system("pause")
#n400-----------------------------------------------------------------------------------------------------                    
                key_word_loc = usr_info.find(key)#注意                
                in_word_len = len(key)#注意
                
                t_key_word_loc = storage_usr_info.find(key) 
                info_word_st_loc[info_word_sum] = t_key_word_loc #注意
                
                #print('对应匹配字符串:',key,'匹配字符串起始位置:',key_word_loc,'匹配字符长度:'
                      #,in_word_len)
                    #d[key] = True
                if key_word_loc + in_word_len == len(usr_info):
                    t_last_kw_loc = usr_info[key_word_loc:]  
                    #print('位置为最后一个字符',usr_info[key_word_loc:])
                    usr_info = usr_info[:key_word_loc]

                    info_word_loc_list[info_word_sum] = t_last_kw_loc
                    #print('最后一个字符更新后的用户信息:',info_word_loc_list)
                    #os.system("pause")
#---------------------------------------------------------------------------------------------------                       
                else:                     
                     usr_info = usr_info[0:key_word_loc]+usr_info[key_word_loc+in_word_len:]#注意
                     #c_key_loc = usr_info 
                     #key_word_loc + in_word_len
                     #print('测试',usr_info)
                     #os.system("pause")
                info_word_loc_list[info_word_sum] = key #注意
                truncation_key_word = usr_info[key_word_loc:key_word_loc+in_word_len]#注意
                #print('关键字截取:',truncation_key_word,key_word_loc,key_word_loc+in_word_len)
                #print('here',usr_info[key_word_loc:key_word_loc+in_word_len],len(usr_info)

                #print("键完全匹配->",key,"值状态位:",value,d[key])
                                  
                #print('更新后的用户信息-state:',usr_info,'>>>>>>>>>',value,d[key])
                print(storage_usr_info)
                #n_state_kw_info = usr_info#注意,保存删除认为无用字符后的信息
                info_word_sum += 1
                #print('暂停',info_word_loc_list)
                #os.system("pause")
                d_state_flag = True
                n_state_info = usr_info
#-------------------------------------------------------------------------------------------------------           
#---------------------------------------------------------------------------------------------------------------       
#-检测状态或关系连接字符是否存在------------------------------------------------------------------------------------------------                 
   #print('检测除第一关键字外关键字列表及起始位置',info_word_loc_list,info_word_st_loc)
   if p_e_flag:
      info_word_loc_list.append(conversion_person)
      #print('反向人称存在',info_word_loc_list)
      #os.system("pause")#info_word_sum += 1
#---------------------------------------------------------------------------------------------------
   for lc,ld in enumerate(d_state_list):          
       #print('最后检测列表内容:',lc,ld)
       for lk,lv in ld.items():

           if lv == True:
              #print('最后检测列表内容:',lk,lv)
              #os.system("pause")
              d_state_no_flag = False
              d_state_h_flag  = True
              break
            
   if d_state_h_flag == True:
        d_state_no_flag = False
   else:
        d_state_no_flag = True
                
   print('注意,列表对应标记位',d_state_no_flag,d_state_h_flag)
   #os.system("pause")
   print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
# if p_kw_special_l_loc == False:#检测关键字特殊位置状态是否有效
   for c,d in enumerate(d_class_list):
          print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
          #print('当前用户信息:',usr_info)
          in_word_len = 0
          t_dc_list = c                    
          #print('关键字列表内容:',c,d)
          #os.system("pause")
          for key,value in d.items():              
              #print('键:',key,"值及类型:",value)
#//////////////////////////////////////////////////////////////////////////////////////////////                   
              if key in usr_info:
                 key_word_sum += 1
                 global_obj_flag = True
                 global_obj_list.append(key)
                 label = '标签'
                 #print('匹配关键字长度及位置:',len(key),key,usr_info.find(key))
                 
                 key_word_loc = usr_info.find(key)
                 key_word_loc_list[key_word_count] = key_word_loc
                 #print('当前关键字位置:',key,key_word_loc_list[key_word_count])
                 
                 in_word_len = len(key) + in_word_len
                 key_word_loc_len_list[key_word_count] = in_word_len
                 #print('当前关键字长度:',key,key_word_loc_len_list[key_word_count])
                 key_word_len_sum = in_word_len + key_word_len_sum
                 #os.system("pause")                 

#///////////////////////////////////////////////////////////////////////////////////////////////                  

                 print(s_p_exist_flag,conversion_usr_info,obj_flag_list,value)   
                 all_kw_flag_list[0] = True
                 
                 t_r = getattr(value,label)()
                 
                 dy_label.append(t_r)
                 
                 first_to_five_label.append(t_r)
                 
                 key_word_label.append(t_r)#单独保存第一关键字标签
                 
                 first_to_five_list.append(key)

                 n_s_del_w_loc = storage_usr_info.find(key)#注意 n_s_del_w_loc
                 info_word_loc_list[info_word_sum] = key#注意
                 info_word_st_loc[info_word_sum] = n_s_del_w_loc#注意 key_word_loc
                 info_word_sum += 1 
                 #print('检测第一关键字插入列表及起始位',info_word_loc_list,info_word_st_loc)
                 #print(first_to_five_list)
                 #os.system("pause")
#---------------------------------------------------------------------------------------------------
                 current_key_word = key#注意
                 key_word_list[key_word_count] = current_key_word
                 key_word_count += 1
#---------------------------------------------------------------------------------------------------
                 attribute_key_word[attribute_key_word_count] = current_key_word
                 #print('转换中间信息解释位:',conversion_usr_info[conversion_count])#注意
                 #print('对应匹配字符串:',key,'匹配字符串起始位置:',key_word_loc)
                 #print('列表序列:',c,"键完全匹配->",key,'匹配字符长度:',in_word_len,"值内容:",value)
                 #print('当前关键字:',current_key_word)
                 #print('输出关键字列表及长度:',key_word_list,key_word_count)
                 #os.system("pause")
#///////////////////////////////////////////////////////////////////////////////////////////////
                 first_kw_flag = True  
                 attribute_key_word_count += 1
                 #key_word_count = 0
                 optimize_count = 0
                 conversion_count = 0
                 current_person_flag_count = 0
                 attribute_key_word_count = 0
                 #k_symbol_flag = False
#-----------------------------------------------------------------------------------------------
                 usr_info = usr_info[0:key_word_loc] + usr_info[key_word_loc+in_word_len:]#注意
                 #print(usr_info)
                 #os.system("pause")

#//////////////////////////////////////////////////////////////////////////////////////////////
              #else:
                  #print('列表序列:',c,"不在匹配范围内!!",'值:',key)
#----------------------------------------------------------------------------------------------
                  
   while optimize_count < key_word_count:#optimize_usr_info                     
              optimize_usr_info = optimize_usr_info + key_word_list[optimize_count]
              optimize_count += 1    
   #print('合成优化后信息:',optimize_usr_info,'关键字列表:',key_word_list)
   #os.system("pause")
#***********************************************************************************************
   if d_state_flag == True:
      i = n_state_info      
      #print('检测',i,usr_info)
      #d_state_flag = False      
   elif d_state_flag == False:
      if p_e_flag == True:
         i = optimize_usr_info
      else:
         i = storage_usr_info#optimize_usr_info
         #print('再看看',i,usr_info,optimize_usr_info)
         #os.system("pause")      
   d_state_flag = False
   #p_e_flag     = False   
   #print('看看',d_state_flag,i,optimize_usr_info)
   #os.system("pause")
#---------------------------------------------------------------------------------------------------
   #info_word_loc_list[info_word_sum] = key#注意
   #info_word_st_loc[info_word_sum] = key_word_loc#注意
   
   print('检测',info_word_st_loc)#n_state_kw_info
   #os.system("pause")
   
   t_w_ori_list = info_word_st_loc
   t_w_list = sorted(info_word_st_loc)
   t_len = len(info_word_st_loc)
   
   w_count = t_len
   w_count -= 1
   t_sum = info_word_sum
   t_count = 0
   
   while info_word_sum < t_len: 
      del t_w_list[t_count]
      #del info_word_loc_list[t_count]
      #print('看这里',t_w_list,t_len)
      info_word_sum += 1
      #t_count += 1
#-------------------------------------------------------------------------------------------------    
   while t_len > t_sum:
      del info_word_loc_list[w_count]
      del t_w_ori_list[w_count]
      #print('再看看',t_w_list)
      t_sum += 1
      w_count -= 1
      
   info_word_st_loc = t_w_list      
   print('完成值大小排序',info_word_st_loc,len(info_word_st_loc),info_word_sum)
   #print('删除字符列表多余元素',info_word_loc_list,t_w_ori_list)
   #print('增加反向人称后的列表',info_word_loc_list)
   #os.system("pause")
#---------------------------------------------------------------------------------------------------   
   t_kw_list = ['']*len(info_word_st_loc)
   
   for tc,tk in enumerate(info_word_st_loc):
        
       for ic,ik in enumerate(t_w_ori_list):
           if tk == ik:
              t_kw_list[tc] = info_word_loc_list[ic]
              #print('排序',t_kw_list,tk,ik,tc,ic)
                 
   info_word_loc_list = t_kw_list
   #info_word_loc_list[0] = 
   #print('更新全部关键字列表',info_word_loc_list)
   #os.system("pause")
   
   for c,d in enumerate(d_state_list):#注意以下代码删除多余无用字符并搜索第一关键字外的关键字状态位

          #print('状态及连接字符列表内容:',c,d)
          for key,value in d.items():
              #print('键:',key,"值:",value)
              for ic,ik in enumerate(info_word_loc_list):
                  if ik == key:
                     if value == False:
                        info_word_loc_list.remove(ik)  
                        #print('找到匹配多余字符并删除',ik,value)
                     #if value == True:
                        #print('找到其他关键字',ik,value)
                        #os.system("pause")

   #print('更新全部关键字列表',info_word_loc_list,key_word_count,key_word_list_content)
   #os.system("pause")
#--------------------------------------------------------------------------------------------------     
 
#*****************************************************************************************************
   #print('关键字总数及总长度:',key_word_sum,key_word_len_sum)
   #print('暂停测试',usr_info,len(usr_info))
   c = 0
   lc = 0
   til = len(usr_info)
   
   if til > key_word_len_sum:#key_word_loc_list[key_word_count]
          
          lc = til - key_word_len_sum
          unidentified_word = usr_info
          #print('信息总长度和关键字总长度及未知字符',key_word_len_sum,til,usr_info)
          unidentified_flag = True#key_word_loc_len_list[key_word_count] unidentified_loc
   unidentified_loc = storage_usr_info.find(unidentified_word)
   
   #print('得到未知字符及其位置:',unidentified_word,unidentified_flag,unidentified_loc)
   info_word_loc_list.insert(unidentified_loc,unidentified_word)
   #print('更新插入位置字符后的列表:',info_word_loc_list)
   
   #os.system("pause")
   l_c = 0
   t_c = 0
            
   r_w = []
   lb_f = False
   
   first_nineteen_kw_l[0] = key_word_list
   print(len(first_nineteen_kw_l),len(all_kw_flag_list))
#///////////////////////////////////////////////////////////////////////////////////////////////////
   if unidentified_flag == True:
      #os.system("pause")   
      oil = len(unidentified_word) - 1
      #print('位置字符长度',oil)#storage_usr_info
      c   = 0
      tc = 0
      tw = ''
      tb = ''
      st = []
      m = False
    
      while c < oil:   

            #print('开始',tw,c,oil)
            tc = c
            #tw = tailor_info[c]


            if m == False:
               tw = tw + unidentified_word[c]
               if tw in storage_usr_info:
                  m = True
                  tb = tw
                  st.append(tb)
                  #print('当前字符匹配',tw,m,st)

            
            elif m == True:
                
               tw = tw + unidentified_word[c+1] 
                    
               if tw in storage_usr_info:                  
                  
                  tb = tw
                  tc += 1
                  c = tc
                  st.append(tb)
                  #print('下一个字符匹配',tw,st)
        
               elif tw not in storage_usr_info:
                    m = False
            
                    #print('不匹配',tw)
                    #st.append(tb)
                    #tf = tailor_info[c+1]
                    tw = ''
                    #print('清除不匹配后的信息,本轮查询结束',tb,st)                    
                    #tc += 1
                    c = tc 
                    st.append(tw)
                    #print('匹配,本次查询结束',c,tw)
           
                    tc += 1
                    c = tc                

   #os.system("pause")
#---------------------------------------------------------------------------------------------------
 
#///////////////////////////////////////////////////////////////////////////////////////////////////
def get_result():

    global key_word_list      
    global conversion_person_key_word #当前人称关键字
    global conversion_usr_info #当前人称关键字列表
    global d_person_match #人称字符串列表
    global person_class_list #人称类列表
    global current_key_word #当前对象关键字
    global successful_flag
    global cause
    global how
    global answer_flag

    global sure_flag
    global none_flag
    global select_flag
    global have_obj
    
    global obj_flag
    global current_key_word_obj
    
    global d_state_h_flag
    global d_state_no_flag
    global n_ksym_kperson
    global time_flag
    global key_word_count
    global unidentified_flag
    global unidentified_word
    global c_kw_flag
    global a_kw_flag
    global current_state_flag

    global s_p_exist_flag
    global obj_flag_c
    global obj_flag_list
    global second_key_word_list
    global second_key_word_c
    global second_kw_flag
    global first_kw_flag
    global four_kw_flag
    global kw_tow_five_list
    global all_kw_flag_list
    global key_word_list_content
    
    global mf_kwc_flag
    global o_kw_key_match
    global o_kw_key_l_match
    global o_kw_key_t_match
    global key_kw_link_flag
    global key_kw_link_c
    global kk_lind_flag
    global ok_obj_fk_flag
    global four_key_word_list
    global all_kw_flag_list
    global kw_tow_five_count
    global skw_m_okw
    global d_okw_class_list
    global okwk_m_fkw
    global second_key_m_word

    global three_key_word_loc_c
    global three_kw_flag
    global three_key_word_c
    global three_key_word_list

    global five_key_word_list
    global five_key_word_lo
    global five_key_word_loc_c
    global five_key_word_c

    global second_kw_flag
    global sk_m_tk_w
    global first_kw_flag
    global fkw_m_tkw_flag
    global five_kw_flag
    global tkw_m_ikw_flag
    global l_m_v
    global max_flag
    global min_flag
    global all_kw_flag_list
    global first_nineteen_kw_l
    global dy_label
    global ot_label

    global seven_c_kw_loc
    global seven_key_word_loc
    global seven_key_word_loc_c
    global seven_key_word_list
    global seven_key_word_c

    global tow_to_five_flag
    global tow_to_five_list
    global tow_to_five_label
    global first_to_five_label
    global model_label

    global front
    global opposite
    
    global k_symbol_flag
    
    global model_kw_list

    global model_training
    global key_word_label
    
    
    global model_kw_label_flag
    global model_kw_label
    global ignore_kw_label
    global o_kw_label_flag
    global dy_kw_model_dict
    
    all_kw_sum = 0
    #global b_key_word_list
    temp_key_word = ''
    temp_skey_word = ''
#k_symbol_flag,c_kw_flag,a_kw_flag,unidentified_flag,s_p_exist_flag,second_kw_flag 参数集合
#first_kw_flag#参数集合
#////////////////////////////////////////////////////////////////////////////////////////////////////    
    g_current_key_word_obj = current_key_word_obj
    get_result = False
    #global obj_flag
    temp_list_count = len(person_class_list) - 1
    obj_attribute = current_key_word
    obj_variable = '对象'    
#//////////////////////////////////////////////////////////////////////////////////////////////////
  
#**************************************************************************************************
#all_kw_flag_list first_nineteen_kw_l

    #print('看这里',all_kw_flag_list,first_nineteen_kw_l)
    t_c = 0
    find_zf_c = 0
    
    kw_m_l = []
    
    for fc,fk in enumerate(all_kw_flag_list):
        if fk == True:
           print('看这里',fk,first_nineteen_kw_l[fc],fc)
           tl = first_nineteen_kw_l[fc]
           t_len = len(first_nineteen_kw_l[fc])
           
           while t_c <t_len:
           
                 for ckc,ckk in enumerate(tl):
                     if ckk == '':
                        tl.remove(ckk)
                 t_c += 1
                 
           t_c = 0
           kw_m_l.append(tl) #model_training            
           
           #print('删除多余长度-all_find_list',kw_m_l,info_word_loc_list,key_word_list_content)
    #print('最后排序及删除多余长度关键字列表',info_word_loc_list)
#///////////////////////////////////////////////////////////////////////////////////////////////////            
    #os.system("pause")
#----------------------------------------------------------------------------------------------------
           
    kwl_c = 0
    fkw = key_word_list_content
    fkw_l = len(key_word_list_content)

    while kwl_c < fkw_l:
          for ckc,ckk in enumerate(fkw):
              if ckk == '':
                 fkw.remove(ckk)
                 #print('删除多余长度-other key word',fkw,ckc)
          kwl_c += 1
          
    key_word_list_content = fkw
    all_kw_sum = len(info_word_loc_list)
    #os.system("pause")  
#lrs-b--判断是否需要贴上非第一关键字标签------------------------------------------------------------------------------------------   
    #if (all_kw_sum >= 4) and (model_kw_sum > 1):#注意，全部关键字总数超出范围就启动模型分析
    print('准备模型分析☞☞☞☞')
    set_label()

#-----------------------------------------------------------------------------------------------------
    obj_variable = '大纲'
    #exclude_kw_list = ['']*key_word_count
    
    nf_kw = key_word_list_content#第二关键字
    nf_kw_len = len(key_word_list_content)
    
    kwl = key_word_list   
    kwl_l = len(kwl)
    kwl_c = 0
    
    ktw = ''
    kwn = ''
    kwf = ''
    all_kw_count = 0
#---------------------------------------------------------------------------------------------------
    while kwl_c < kwl_l:
          for ckc,ckk in enumerate(kwl):
              if ckk == '':
                 kwl.remove(ckk)
                 #print('删除多余长度-first key word',kwl,ckc)
          kwl_c += 1          
    key_word_list = kwl
    #info_word_loc_list key_word_count k_symbol_flag        
#--------------------------------------------------------------------------------------------------
    kwl_c = 0
    while kwl_c < nf_kw_len:
          for ckc,ckk in enumerate(nf_kw):
              if ckk == '':
                 nf_kw.remove(ckk)
                 #print('删除多余长度-second first key word',nf_kw,ckc)
          kwl_c += 1          
    key_word_list_content = nf_kw
    #print(key_word_list_content)
    #os.system("pause") #key_word_list ,key_word_list_content ,info_word_loc_list
#--------------------------------------------------------------------------------------------------
    kwl_c = 0
    fkw = five_key_word_list
    fkw_l = len(five_key_word_list)
    
    if all_kw_flag_list[4] == True:
          
       while kwl_c < fkw_l:
          for ckc,ckk in enumerate(fkw):
              if ckk == '':
                 fkw.remove(ckk)
                 #print('删除多余长度-five key word',fkw,ckc)
          kwl_c += 1
          
    five_key_word_list = fkw
    #os.system("pause")
    #print(key_word_list_content)

    #all_kw_flag_list[3] four_key_word_list
#--------------------------------------------------------------------------------------------------
    kwl_c = 0
    fkw = three_key_word_list
    fkw_l = len(three_key_word_list)
    
    if three_kw_flag == True:
          
       while kwl_c < fkw_l:
          for ckc,ckk in enumerate(fkw):
              if ckk == '':
                 fkw.remove(ckk)
                 #print('删除多余长度-three key word',fkw,ckc)
          kwl_c += 1
          
    three_key_word_list = fkw
#--------------------------------------------------------------------------------------------------
       
#--------------------------------------------------------------------------------------------------    
    list_dir = '大纲'
    kwl_c = 0
    all_dir = ''
    all_n_dir = ''
    #n_reurn_count = ''
    
    list_kw = []
    list_kw_c = 0
    sck_f = False
    ck_f  = False
    kw_m_c = 0
    
    if key_word_count > 1 and second_kw_flag == True:# or key_word_count == 1:

            
       for kwc,kwk in enumerate(key_word_list):#kwl key_word_list info_word_loc_list
                  #if kc == kwk:
           ktw = key_word_list[0:kwc] + key_word_list[kwc+1:]
                     
           #kwn = kwk#注意
           #kwf = ktw[0]#注意
           
           
           #print('测试',kwk,kwf,key_word_list_content)

           #os.system("pause")
           for cec,cek in enumerate(d_class_list):
               for cfc,cfk in cek.items():
                   if cfc == kwf:                         
#-------------------------------------------------------------------------------------------------------------                     
                      all_dir = getattr(cfk(),list_dir)()
                             
                      for asc,sck in enumerate(all_dir):
                          t_reurn_count = getattr(cfk,sck)()
                          for dvc,dvk in t_reurn_count.items():
                              print('大纲内容函数返回值dvc',dvc)
                              #os.system("pause")
                              for fcc,fck in enumerate(key_word_list_content):
#-------------------------------------------------------------------------------------------------------------                             
#-------------------------------------------------------------------------------------------------------------                                   
                              #for lc,lk in enumerate(kwf):
                                  #for clc,clk in enumerate(d_class_list):
                                      #for cnc,cnk in clk.items():
                                          #if cnc == lk:
  
#-------------------------------------------------------------------------------------------------------------                                        all_n_dir = getattr(eval(lk)(),list_dir)(
                                             #all_n_dir = getattr(cnk(),list_dir)()
                                             
                                             #for ac,ck in enumerate(all_n_dir):
                                                   
                                                 #n_reurn_count = getattr(cnk,ck)()
    
                                                 #for nc,nk in n_reurn_count.items():
                                                     #print('大纲内容函数返回值kwf',nc)
                                                     
                                                     #if kwk == dvc:
                                                        #kk_lind_flag = True
                                                        #list_kw.append(sck)
                                                        #print('第一关键字(键)互相链接成功'
                                                              #,#sck,nc,dvc,cnc)
                                                        #os.system("pause")
                                                        #for cc,ck in enumerate(key_word_list_content):
                                                            #if dvc == ck:
                                                               #o_kw_key_l_match = True
                                                               #second_key_m_word = ck
                                                               #print('第一关键字键互相链接->匹配非第一关键字字成功',ck,kwk)
                                                               #os.system("pause")
                                                               #break

                                if dvc == kwk:
                                   list_kw.append(sck)   
                                   kw_m_c += 1
                                         
                                   key_kw_link_flag = True
                                   temp_skey_word = dvc# 
                                   second_key_m_word = dvc
#以下代码限制第一关键字键链接其它第一关键字总数为2个------------------------------------------
                                                       
#---------------------------------------------------------------------------------------------------     
               
                                   #print('第一关键字(键)->第一关键字链接成功',sck,kwk,list_kw)#lk
                                   print(kw_m_c,kwk,kwf,sck)

                                elif dvc == fck:#此处之前有错误dc变量需要查找来源
                                     o_kw_key_t_match = True
                                     #print('链接->匹配非第一关键字成功',sck,fck,kwk)
                                     #os.system("pause")
#-----------------------------------------------------------------------------------------------------
                                     for clc,ckk in enumerate(d_okw_class_list):
                                         for cnc,cfk in ckk.items():
                                             if cnc == fck:
                                                #print(fck)   
  
                                                klc_return =getattr(eval(fck)(),list_dir)()
                                                for kc,kk in enumerate(klc_return):
                                                     c_return =getattr(eval(fck),kk)()
                                                     for qc,qk in c_return.items():
                                                          if qc == kwk:
  
                                                             ok_obj_fk_flag = True
                                                             second_key_m_word = kwk
                                                             #print('第二关键字找到对应目标第一关键字',fck,kwk)
                                                             #os.system("pause")
                                                             break
                                                          
#------------------------------------------------------------------------------------------------------------------                                                                           
    elif key_word_count == 1 and second_kw_flag == True:
         #os.system("pause") 
         for kwc,kwk in enumerate(key_word_list):#kwl key_word_list info_word_loc_list
                  #if kc == kwk:
             ktw = key_word_list[0:kwc] + key_word_list[kwc+1:]
                     
             kwn = kwk#注意
             kwf = ktw#注意

                     #os.system("pause")
             for clc,clk in enumerate(d_class_list):
                 for cnc,cnk in clk.items():
                     if cnc == kwn:
#--------------------------------------------------------------------------------------------------                     
                        all_dir = getattr(cnk(),list_dir)()
                             
                        for ac,ck in enumerate(all_dir):
                            print(cnk,ck)
                            t_reurn_count = getattr(cnk,ck)()
                            for dc,dk in t_reurn_count.items():
                                #print('大纲内容函数返回值-skw',dc)
#--------------------------------------------------------------------------------------------------
                                for lc,lk in enumerate(key_word_list_content):
                                    if dc == lk:
                                       skw_m_okw = True   
                                       #print('第一关键字(键)匹配非第一关键字',lk)
                                       break
#----d_okw_class_list----------------------------------------------------------------------------------------------

             for clc,clk in enumerate(key_word_list_content):
                 
                 for clc,ckk in enumerate(d_okw_class_list):
                     for cnc,cfk in ckk.items():
                         if cnc == clk:  
                            
                            all_dir = getattr(cfk(),list_dir)()
                 
                            for cnc,cnk in enumerate(all_dir):
                                sum_dir = getattr(cfk,cnk)()
                                for sc,sk in sum_dir.items():                           
                                    if sc == kwn:
                                       okwk_m_fkw = True     
                                       #print('非第一关键字(键)匹配第一关键字键',clk,sc)
                                       #os.system("pause")
                                       break
#-----------------------------------------------------------------------------------------------------                     

#------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------  
    #key_word_list ,key_word_list_content ,info_word_loc_list,o_kw_key_match,ok_obj_fk_flag
    
    #print(kw_m_c)
    #os.system("pause")

    #print('全部关键字列表',key_word_list,tow_to_five_list,key_word_list_content,temp_key_word,kk_lind_flag
          #,o_kw_key_match,ok_obj_fk_flag,o_kw_key_l_match,key_kw_link_flag,temp_skey_word
          #,four_key_word_list,second_kw_flag,three_kw_flag,three_key_word_list,k_symbol_flag)
    #os.system("pause")
    b_key_word_list = key_word_list
#开始获取/分析第一离关键字位置最近的其他关键字#----three_key_word_list-----------------------------------------------------------------------------------------------
    tk_loc = len(three_key_word_list)
    tk_loc_c = 0
    
    fk_loc = len(key_word_list)
    
    sk_loc = len(key_word_list_content)
    sk_loc_c = 0
       
    fk_loc_c = 0
    
    m_okw_list = ['']*tk_loc
    f_kw_list  = ['']*fk_loc
    s_kw_list  = ['']*sk_loc
    
    loc_c = [None]*fk_loc
    loc_cc = 0
    
    td = 0
    md = 0
#---------------------------------------------------------------------------------------------------
    if (three_kw_flag == True and second_kw_flag == True):#注意
       #print('其他等待配对位置的关键字存在 ',three_kw_flag)
       
       for mc,mk in enumerate(info_word_loc_list):
  
           for tc,tk in enumerate(three_key_word_list):             
               if mk == tk:
                  m_okw_list[tk_loc_c] = mc
                  
                  tk_loc_c += 1
                  
                  #print('第三关键字位置:',m_okw_list,tk)
                  
       tk_loc = len(m_okw_list)           
       #print('看这里',m_okw_list,tk_loc)#m_okw_list -- 第三关键字位置
       #os.system("pause")
#-------------------------------------------------------------------------------------------------                  
       for mtc,mtk in enumerate(info_word_loc_list):
             
           for ttc,ttk in enumerate(key_word_list):
               if mtk == ttk:
                            
                  f_kw_list[fk_loc_c] = mtc
                  fk_loc_c += 1
                           
       fk_loc = len(f_kw_list)
       #print('第一关键字位置:',f_kw_list,ttk)#第一关键字位置 -- f_kw_list 
       #print('看这里',f_kw_list,fk_loc)
       #os.system("pause")
#---------------------------------------------------------------------------------------------------
       for mtc,mtk in enumerate(info_word_loc_list):
           for ttc,ttk in enumerate(key_word_list_content):
               if mtk == ttk:
                            
                  s_kw_list[sk_loc_c] = mtc
                  sk_loc_c += 1
                           
       sk_loc = len(s_kw_list)
       #print('第二关键字位置:',s_kw_list,ttk)#第二关键字位置 -- s_kw_list
       #print('看这里',s_kw_list,sk_loc)
       #os.system("pause")
#此段代码查询配对第二关键字/第三关键字---------------------------------------------------------------------------------------------------       
       compare_r_c = 0
       compare_r = [None]*tk_loc

       for rc,rk in enumerate(s_kw_list):
                 
           for tc,tk in enumerate(m_okw_list): 
               td = rk - tk
               if td < 0:
                  td = 0 - td
                  print('转换',td)
                  compare_r[compare_r_c] = td
                  compare_r_c += 1
               else:
                  compare_r[compare_r_c] = td
                  compare_r_c += 1
                     
           #print('比较结果T=F',compare_r,min(compare_r))
           md = min(compare_r)
           #os.system("pause")

            
           for mc,mk in enumerate(compare_r):
               if md == mk:
                  sk_m_tk_w = info_word_loc_list[m_okw_list[mc]]#注意
                  #print('对应位置关键字',sk_m_tk_w)#
                                   
          
           for dc,ck in enumerate(compare_r):#three_key_word_list
               if ck == md:
                  tc = f_kw_list[dc]   
                  #print('找到',md,'位置',dc,'对应第二键字',key_word_list_content)
                  #os.system("pause")
#---------------------------------------------------------------------------------------------------
       compare_r_c = 0
       compare_r = [None]*fk_loc
       
       if tk_loc < fk_loc:#注意

             
            for rc,rk in enumerate(f_kw_list):
                 
               for tc,tk in enumerate(m_okw_list): 
                   td = rk - tk
                   if td < 0:
                      td = 0 - td
                      print('转换',td)
                      compare_r[compare_r_c] = td
                      compare_r_c += 1
                   else:
                      compare_r[compare_r_c] = td
                      compare_r_c += 1                                                
                     
            print('比较结果F>T',compare_r,min(compare_r))
            md = min(compare_r)
            
           
            for dc,ck in enumerate(compare_r):#three_key_word_list
                if ck == md:
                   tc = f_kw_list[dc]   
                   #print('找到',md,'位置',dc,'对应第一关键字',info_word_loc_list[tc])
            #os.system("pause")
#--------------------------------------------------------------------------------------------------                  
       #info_word_loc_list
                 
       elif tk_loc >= fk_loc  and second_key_word_c == 1:#注意
             
            tkw_l = len(three_key_word_list)
            t_count_c = 0#
            t_w_sum = ['']*len(three_key_word_list)#
            #fkw_l = len(three_key_word_list)
            #if fkw_l > 1:
#--------------------------------------------------------------------------------------------------               
            for itc,itk in  enumerate(info_word_loc_list):
                for ttc,ttk in  enumerate(three_key_word_list):
                    if itk == ttk:
                       t_w_sum[t_count_c] = ttk
                       t_count_c =+ 1
                       print('匹配-排序',ttk)
                       
            three_key_word_list = t_w_sum       
            #print('排序结果TKW',three_key_word_list)
            #os.system("pause")            
#---------------------------------------------------------------------------------------------------
            print('第一关键字总数为1第二关键字总数为1第三关键字总数大于或第一关键字') 
            #os.system("pause") 
            compare_r = [None]*tk_loc
            
            
            for rc,rk in enumerate(m_okw_list):
                 
               for tc,tk in enumerate(f_kw_list): 
                   td = rk - tk
                   if td < 0:
                      td = 0 - td
                      print('转换',td)
                      compare_r[compare_r_c] = td
                      compare_r_c += 1
                   else:
                      compare_r[compare_r_c] = td
                      compare_r_c += 1
                     
            #print('比较结果T>F',compare_r,min(compare_r))
#---------------------------------------------------------------------------------------------------
            md = min(compare_r)

            
            #for mc,mk in enumerate(compare_r):
                #if md == mk:
                   #print('对应位置第三关键字',mc,info_word_loc_list[m_okw_list[mc]])#
                                   
          
            #for dc,ck in enumerate(compare_r):#three_key_word_list
                #if ck == md:
                   #tc = f_kw_list[dc]   
                   #print('找到',md,'位置',dc,'对应第一键字',key_word_list)
                   
                   
            #os.system("pause")
#以下代码区域开始分析相应的各关键字得到答案,第三关键字总数被限制在2个-----------------------------------
#key_word_list-three_key_word_list-------------------------------------------------------------------------------------------------
            print(key_word_list,key_word_list_content,three_key_word_list)
            dir_list = '大纲'
            t_f_kw = key_word_list[0]
            fkw_m_tkw_c = 0
            
            #for koc,kok in enumerate(key_word_list):
      
            for dlc,dlk in enumerate(d_class_list):
                      
                for dnc,dnk in dlk.items():
                      
                    if dnc == t_f_kw:
                       print(dnc)
                       
                       dl_r = getattr(dnk(),dir_list)()
                       for rc,rk in enumerate(dl_r):
                           d_v = getattr(dnk,rk)()  
                           for rnc,rnk in d_v.items():
                               #print(rnc)
                               for sc,sk in enumerate(key_word_list_content):
                                   if sk == rnc:
                                      o_kw_key_t_match = True#注意   
                                      #print('第一关键字对应第二关键字',sk)
#----------------------------------------------------------------------------------------------------
                    
                       dt_r = getattr(dnk(),dir_list)()                         
                                
                       for trc,trk in enumerate(dt_r):
                             
                           td_v = getattr(dnk,trk)()
                           
                           for tc,tk in enumerate(three_key_word_list):
                               #print(tk) 
                               for tnc,tnk in td_v.items():
                                 
                               
                                   if tnc == tk:
                                      fkw_m_tkw_c += 1 
                                      fkw_m_tkw_flag = True  
                                      #print('第一关键字对应第三关键字',tk,trk,fkw_m_tkw_c)                                  
                       #print(three_key_word_list,fkw_m_tkw_c)
                       if tkw_l > 1:
                          obj_fan = '特性'
                          t_f_kw = key_word_list[0]
                          t_t_kw = three_key_word_list[1]#第三关键字总数被限制在2个,如多出需修改代码
#--------------------------此处算法将删除第一个第三关键字不做分析,只分析最后一个第三关键字---------
                          print(t_t_kw)
                          for olc,olk in enumerate(d_okw_class_list):
                      
                              for onc,onk in olk.items():
                      
                                  if onc == t_t_kw:
                                        
                                     r_o_f = getattr(onk,obj_fan)(key_word_list)
                                     print('返回值',r_o_f,key_word_list)
                                     r_m = getattr(eval(t_f_kw),r_o_f)()
                                     print(r_m)
                                     for rcc,rkk in r_m.items():
                                         if rcc == t_t_kw:
                                            print(rkk)
                                            #os.system("pause")

                       else:#以下代码是分析只有一个第三关键字的情景
                           #os.system("pause")
                            obj_fan = '特性'
                            t_f_kw = key_word_list[0]
                            t_t_kw = three_key_word_list[0]
                            
                            for olc,olk in enumerate(d_okw_class_list):
                      
                              for onc,onk in olk.items():
                                  for otc,otk in enumerate(three_key_word_list):  
                      
                                      if onc == otk:
                                         
                                         r_o_f = getattr(onk,obj_fan)(key_word_list)
                                         #print('返回值',r_o_f,otk,key_word_list)
                                         r_m = getattr(eval(t_f_kw),r_o_f)()
                                         print(r_m)
                                         #os.system("pause")
                                         for rcc,rkk in r_m.items():
                                             if rcc == t_t_kw:
                                                print(rkk)
                                                #os.system("pause")
                                      
                       #os.system("pause")  

#---------------------------------------------------------------------------------------------------
    
#---------------------------------------------------------------------------------------------------
       #m_okw_list f_kw_list 
       elif key_word_count == three_key_word_c:
             
            #os.system("pause")
            #print('第一关键字和第三关键字总量一致',three_key_word_list
                  #,key_word_list,key_word_list_content,info_word_loc_list)
            
            if second_kw_flag == True:#注意
                  
               t_arrange = ['']*len(three_key_word_list)
               t_arrange_c = 0

               k_arrange = ['']*len(key_word_list)
               k_arrange_c = 0

               s_arrange = ['']*len(key_word_list_content)
               s_arrange_c = 0

               for ic,ik in  enumerate(info_word_loc_list):
                   for tc,tk in  enumerate(three_key_word_list):
                       if ik == tk:
                          t_arrange[t_arrange_c] = tk
                          t_arrange_c =+ 1
                          #print('匹配-排序',tk)

               three_key_word_list = t_arrange       
               #print('排序结果TKW',three_key_word_list)
#---------------------------------------------------------------------------------------------------
               for ic,ik in  enumerate(info_word_loc_list):
                   for tc,tk in  enumerate(key_word_list):
                       if ik == tk:
                          k_arrange[k_arrange_c] = tk
                          k_arrange_c =+ 1
                          #print('匹配-排序',tk)
                          
               key_word_list = k_arrange       
               #print('排序结果FKW',key_word_list)

#---------------------------------------------------------------------------------------------------
               for ic,ik in  enumerate(info_word_loc_list):
                   for tc,tk in  enumerate(key_word_list_content):
                       if ik == tk:
                          s_arrange[s_arrange_c] = tk
                          s_arrange_c =+ 1
                          print('匹配-排序',tk)
                          
               key_word_list_content = s_arrange      
               #print('排序结果SKW',key_word_list_content)
               #os.system("pause")
#以下代码开始分析获取答案---------------------------------------------------------------------------------------------------            
               one_kt_v_list = []
               tow_kt_v_list = []
               tt_kt_v_list  = []

               one_kt_f = False
               tow_kt_f = False
               tt_kt_f  = False
               #以上三个列表定义是限制第一关键字最多为3个
               t_st_v_list = []
               t_st_v_c = 0
               
               dir_list = '大纲'
               all_dir = ''
               
               f_t_kw_l = len(key_word_list)-1
               s_t_kw_l = len(key_word_list_content)-1
               #tkw_l = len(three_key_word_list)
               
               while f_t_kw_l >= 0:
                     #print('F-T测试',key_word_list[f_t_kw_l],three_key_word_list[f_t_kw_l])
                     
                     if f_t_kw_l == 0:
                        #print('看看',f_t_kw_l)
                        t_f_kw = key_word_list[f_t_kw_l]
                        t_t_kw = three_key_word_list[f_t_kw_l]
                        print(t_f_kw,t_t_kw)
#--------------------------------------------------------------------------------------------------
                        for cec,cek in enumerate(d_class_list):
                            for cfc,cfk in cek.items():
                                if cfc == t_f_kw:
                                   #print('找到关键字',cfc)   
#-------------------------------------------------------------------------------------------------------------                     
                                   all_dir = getattr(cfk(),dir_list)()
                                   #print('查看0',t_f_kw,t_t_kw)
                                   
                                   for asc,sck in enumerate(all_dir):
                                         
                                       t_reurn_count = getattr(cfk,sck)()
                                       
                                       for dvc,dvk in t_reurn_count.items():
                                           #print('大纲内容函数返回值',sck,dvc,t_t_kw)
                                           if dvc == t_t_kw:
                                              one_kt_v_list.append(dvk)
                                              #one_kt_v_c += 1
                                              #print('对应关键字-(键)匹配',t_t_kw,sck)
                                              #print('列表内容',one_kt_v_list)
                                              #os.system("pause")
#--------------------------------------------------------------------------------------------------                        
                     elif f_t_kw_l == 1:
                        #print('看看',f_t_kw_l)
                        t_f_kw = key_word_list[f_t_kw_l]
                        t_t_kw = three_key_word_list[f_t_kw_l]
                        print(t_f_kw,t_t_kw)
#---------------------------------------------------------------------------------------------------
                        for cec,cek in enumerate(d_class_list):
                            for cfc,cfk in cek.items():
                                if cfc == t_f_kw:
#-------------------------------------------------------------------------------------------------------------                     
                                   all_dir = getattr(cfk(),dir_list)()
                                   #print('查看1',t_f_kw,t_t_kw)
                                   
                                   for asc,sck in enumerate(all_dir):
                                       t_reurn_count = getattr(cfk,sck)()
                                       for dvc,dvk in t_reurn_count.items():
                                           #print('大纲内容函数返回值',dvc,t_t_kw)
                                           if dvc == t_t_kw:
                                              tow_kt_v_list.append(dvk)   
                                              #print('对应关键字-键匹配',tow_kt_v_list)
                                              #os.system("pause")
                                              
#-------------------------------------------------------------------------------------------------------------                                                                       
                        
                     elif f_t_kw_l == 2:
                        #print('再看看',f_t_kw_l)
                        t_f_kw = key_word_list[f_t_kw_l]
                        t_t_kw = three_key_word_list[f_t_kw_l]
                        print(t_f_kw,t_t_kw)
#---------------------------------------------------------------------------------------------------
                        for cec,cek in enumerate(d_class_list):
                            for cfc,cfk in cek.items():
                                if cfc == t_f_kw:
#-------------------------------------------------------------------------------------------------------------                     
                                   all_dir = getattr(cfk(),dir_list)()
                                   #print('查看2',t_f_kw,t_t_kw)
                                   
                                   for asc,sck in enumerate(all_dir):
                                       t_reurn_count = getattr(cfk,sck)()
                                       for dvc,dvk in t_reurn_count.items():
                                           #print('大纲内容函数返回值',dvc,t_t_kw)
                                           if dvc == t_t_kw:
                                              tt_kt_v_list.append(dvk)   
                                              #print('对应关键字-键匹配',tt_kt_v_list)
                                              #os.system("pause")                        

                     f_t_kw_l -= 1              
#-------------------------------------------------------------------------------------------------------------                
               
               while s_t_kw_l >= 0:
                     print('S-T',key_word_list_content[s_t_kw_l],sk_m_tk_w)
                     t_s_kw = key_word_list_content[s_t_kw_l]
#---------------------------------------------------------------------------------------------------
                     for cec,cek in enumerate(d_okw_class_list):
                         for cfc,cfk in cek.items():
                             if cfc == t_s_kw:
                                #print('测试',t_s_kw)
                                #os.system("pause")
#-------------------------------------------------------------------------------------------------------------                     
                                all_dir = getattr(cfk(),dir_list)()#three_key_word_c
                                #print('查看S-T',sk_m_tk_w)
                                   
                                for asc,sck in enumerate(all_dir):
                                    t_reurn_count = getattr(cfk,sck)()
                                    for dvc,dvk in t_reurn_count.items():
                                        #print('大纲内容函数返回值',dvc,t_t_kw)
                                        if dvc == sk_m_tk_w:
                                           t_st_v_list.append(dvk)  
                                           #print('对应第三关键字-键匹配',t_st_v_list,dvc)
                                           #os.system("pause")
                     s_t_kw_l -= 1
#---------------------------------------------------------------------------------------------------
               #one_kt_v_list tow_kt_v_list
               print(one_kt_v_list,tow_kt_v_list)
               #os.system("pause") 
               '''for oc,ok in enumerate(one_kt_v_list):
                   for soc,sok in enumerate(ok):
                 
                       for ttc,ttk in enumerate(tow_kt_v_list):
                           for tc,tk in enumerate(ttk): '''   

                               #if sok == tk:
                                  #print('找到F',sok)
                                  #os.system("pause")
                           
                               #elif tk in sok:
                                  #print('找到T',ttk)
                                  #os.system("pause")  

                               #elif sok in tk:
                                  #print('找到S',sok)
                                  #os.system("pause")
                           
                                  
#---------------------------------------------------------------------------------------------------
    if three_kw_flag == False and first_kw_flag == True and second_kw_flag == True:
       print('不存在第三关键字',kk_lind_flag,key_word_list_content)
       
       if kk_lind_flag == True:#o_kw_key_l_match(o_kw_key_l_match,o_kw_key_t_match,o_kw_key_match,ok_obj_fk_flag,)
          #print('第一关键字(键)*互相链接存在',key_kw_link_flag)#key_word_list_content
          print(o_kw_key_l_match,o_kw_key_t_match,o_kw_key_match,ok_obj_fk_flag,)       
          
          if key_kw_link_flag == True:
             print('第一关键字(键)-->第一关键字链接存在')#o_kw_key_match->ok_obj_fk_flag
             
             if o_kw_key_l_match == True or o_kw_key_t_match == True:
                print('第二关键字匹配第一关键字(键)')#后续执行代码需补充
                ##后续执行代码需补充
             else:
                print('准备分析第二关键字')
                t_p_w = '特性'

                
                for sc,sk in enumerate(key_word_list_content):
                    r_w = getattr(eval(sk),t_p_w)(list_kw)
                    print(r_w)
                
             
       #key_kw_link_flag o_kw_key_t_match       
          
       elif key_kw_link_flag == True:#o_kw_key_t_match
            #print('第一关键字(键)-->第一关键字链接存在',o_kw_key_l_match,o_kw_key_t_match
                  #,ok_obj_fk_flag)

            if o_kw_key_t_match == True:
                  
               r_kl = []
               r_key_word_list = key_word_list
               
               
               #print('准备分析第二关键字OKKM',list_kw,key_word_list)
               #os.system("pause")
               t_p_w = '特性'
               
               for sc,sk in enumerate(key_word_list_content):
                    r_w = getattr(eval(sk),t_p_w)(list_kw)
                    #print('返回准备查询路径列表',r_w)
                    #os.system("pause")
                    
               #r_len  = len(r_w)
               #kw_len = len(r_key_word_list)     
                    
               #if r_len < kw_len:
 
                  #r_key_word_list.pop()
               #print('测试',r_key_word_list,b_key_word_list)

               for rkc,rkk in enumerate(key_word_list):
                   for dec,dek in enumerate(d_class_list):
                       for dfc,dfk in dek.items():
                           if dfc == rkk:
                              print('匹配关键字',rkk)
                              
                              for erc,erk in enumerate(r_w):
                                  er_o = getattr(dfk,erk)()
                                  print('返回值',er_o)
                                  #以下代码只处理了其中一个返回值的字典查询，另一个需补充处理
                                  for fec,fek in er_o.items():
                                      print(fec)
                                      #os.system("pause")
                                      if fec in storage_usr_info:
                                         ft_ok = fec
                                         ft_ov = fek
                                         print('找到',ft_ok,ft_ov)
                                             
                                      else:
                                         for gec,gek in enumerate(key_word_list):
                                             print(gek,key_word_list)  
                                             #os.system("pause")
                                                  
                                             if gek in fec:
                                                    
                                                print('看这里',fek)
                                                break
                                    
                  
                     
                                  
                                    
            #if o_kw_key_l_match == True or o_kw_key_t_match == True:
               #print('准备分析第二关键字OKKLM')
               print(storage_usr_info)                   
               
            else:
               pass
                   
             
#----------------------------------------------------------------------------------------------------
    if three_kw_flag == True and second_kw_flag == False and first_kw_flag == True and five_kw_flag == False:
       print('不存在第二关键字')
       
       
    if three_kw_flag == True and second_kw_flag == True and first_kw_flag == False:
       print('不存在第一关键字')

    if fk_loc > tk_loc  and five_kw_flag == True and first_kw_flag == True:#注意
       #以下代码限制第三关键字总数在1个   
       dir_list = '大纲'
       t_m_kw_c = 0
       r_f_v = ''
       r_c = []
       t_d = []
       t_t_kw = three_key_word_list[0]#
       
       print('不存在第二关键字,存在第一及第三第五关键字,而且第一关键字总数大于第三关键字')
       #print(three_key_word_list,five_key_word_list,key_word_list)
       #os.system("pause")
       for dc,dk in enumerate(d_class_list):
           for dfc,dfk in dk.items():
               for fkc,fkk in enumerate(key_word_list):
                   if fkk == dfc:
                      #t_m_kw_c   
                      print('匹配',dfc)
                      
                      r_l = getattr(dfk(),dir_list)()

                      #for rc,rk in enumerate(r_l):
  
                          #r_d = getattr(dfk,rk)()
                          #for ec,ek in r_d.items():
                              #if ec == t_t_kw:
                                 #fkw_m_tkw_flag = True   
                                 #print('对应',ec)
                                 
       if fkw_m_tkw_flag == True:
          features = '特性'
              
          for fc,fk in enumerate(d_okw_class_list):
               for fnc,fnk in fk.items():
                   for ffc,ffk in enumerate(five_key_word_list):
                       if ffk == fnc:
                           tkw_m_ikw_flag = True  
                           print('看到',fnc)
                           r_f_v = getattr(eval(fnc),features)(three_key_word_list)
                           print(r_f_v)
                           
                           #break
                           
       if tkw_m_ikw_flag == True:  
          
          for dc,dk in enumerate(d_class_list):
              for dfc,dfk in dk.items():
                  for fkc,fkk in enumerate(key_word_list):
                      if fkk == dfc:
                         print('再查',dfc,r_f_v)
                         
                         r_l = getattr(dfk(),dir_list)()

                         for rc,rk in enumerate(r_l):
  
                             r_d = getattr(dfk,rk)()
                             for ec,ek in r_d.items():
                                 if ec == r_f_v:
                                    t_m_kw_c += 1
                                    r_c.append(ek)
                                    l_m_v = True   
                                    fkw_m_tkw_flag = True   
                                    print('再对应',ec,r_c)
                                    
       if l_m_v == True:
          print('开始',r_c)
          for rc,rk in enumerate(r_c):
              
              t_d.append(int(rk[0]))
              print(t_d,key_word_list)
              if max_flag == True:
                 max_min = max(t_d)
                 
              elif min_flag == True:
                 max_min =min(t_d)   
              #print(max_min)
              for tc,tk in enumerate(t_d):
                  if max_min == tk:
                     print(max_min,key_word_list[tc])
       
    
#---------------------------------------------------------------------------------------------------
#k_symbol_flag,kk_lind_flag,o_kw_key_l_match,key_kw_link_flag,o_kw_key_l_match,ok_obj_fk_flag
#skw_m_okw,okwk_m_fkw,sk_m_tk_w                   

    if obj_flag == False:
        #print('原因标记位:',cause)
        #os.system("pause")
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
#////////////////////////////////////////////////////////////////////////////////////////////////                          

#////////////////////////////////////////////////////////////////////////////////////////////////
    else:
        #os.system("pause")
        obj_variable = '对象'
        
        while temp_list_count >= 0:
               temp_list_count -= 1
               p = person_class_list[temp_list_count]
               
               successful_flag = getattr(p,obj_variable)(conversion_person_key_word)
               print('人称-对象标志位',conversion_person_key_word,successful_flag,p)#注意这个返回变量
               #os.system("pause")
               if successful_flag == 1:
                  break
#///////////////////////////////////////////////////////////////////////////////////
    if successful_flag == 1:
         #os.system("pause")
#///////////////////////////////////////////////////////////////////////////////////
         p_obj = person_class_list[temp_list_count]#后续要更改此处变量代码
         #print(p_obj)
         #os.system("pause")
         obj_variable = '属性'
#------------------------------------------------------------------------------------------------

         g_current_key_word_obj = getattr(p_obj,obj_variable)(key_word_list,how,cause,
                                                unidentified_flag,unidentified_word,result)

         print(g_current_key_word_obj)
         #os.system("pause")
         print(d_state_no_flag,d_state_h_flag,n_ksym_kperson)
         d_state_no_flag = False
         d_state_h_flag  = False
         n_ksym_kperson  = False
         unidentified_flag = False
         s_p_exist_flag  = False
         four_kw_flag = False
         p_e_flag = False
         key_word_count  = 0
      
         print('运行完成退出',key_word_list,conversion_usr_info,conversion_person_key_word
               ,info_word_loc_list)#info_word_loc_list
    else:
          obj_variable = '属性'
          print(d_state_no_flag,d_state_h_flag,n_ksym_kperson)
          if d_state_no_flag == True:
                if n_ksym_kperson == False:
                   print(current_key_word)
                   #os.system("pause")
                   
                   #g_current_key_word_obj = getattr(eval(current_key_word),obj_variable)(current_key_word)
                   print('来看这里',g_current_key_word_obj)
                   
                elif n_ksym_kperson == True:
                      pass
                     #no_sure(current_key_word) 
          
          d_state_no_flag = False
          d_state_h_flag  = False
          n_ksym_kperson  = False
          key_word_count  = 0
          unidentified_flag = False  
          s_p_exist_flag  = False
          four_kw_flag = False
          p_e_flag = False
          #for cc,ck in enumerate(current_state_flag):
              #print('检测标志位',cc,ck)
          print('对象不匹配，停止',conversion_usr_info,obj_flag,key_word_list
                ,second_key_word_list,three_key_word_list
                ,conversion_person_key_word,conversion_usr_info,info_word_loc_list)

#/////////////////////////////////////////////////////////////////////////////////////////////////          
def wait_usr_info():
      
    global file_line_list
    global usr_info
    global goon_flag
    
    exit_ecs = True
    key_v = ''
    
    #print('开始读取知识库✪✪✪✪✪')
        
    while exit_ecs:

          #else:  
          goon_flag = True
          usr_in()
          search_key_word()
          get_result()
          init_var()
        
    '''goon_flag = True
    usr_in()
    search_key_word()
    get_result()
    init_var()'''
    
#//////////////////////////////////////////////////////////////////////////////////////////////////
wait_usr_info()
#file_r()
#goon_flag = True 
#usr_in()
#file_w()
#search_key_word()
#get_result()
#init_var()


#usr_in()
#search_key_word()
#get_result()


