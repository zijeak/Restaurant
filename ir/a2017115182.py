"""***************************************************************************

                               a2017115182.py

This is a program which can manage restaurants in mongodb database named"test'
and collection named'restaurant'.You can search,add restaurants in GUI program.
You can alse import your own data from a json file.

***************************************************************************"""

"""
To run this program, start python in c:\2017115182\ir and then type:
from a2017115182 import *

1.Before run this program,please check whether you had install some modules,
  such as pymongo.
2.You can click the button "Search" on left side directly,it will show you all
  the restaurants in database you created before.(The database must be named
   "test"
  and the collection must be named "restaurant".)
3.You can double-click a item in the table,it will open a new window to
  show the details of the restaurant you selected.
4.You can use the menu at the top of main window named "Open" to import 
  your own data in a json file.It will take some seconds,please wait a 
  monment until a notice dialog appeared in the center of screen.
  Remember:If you imported your own data,the data in database before will 
  be cleared!
5.You can also use the menu at the top of main window named "New" 
  to add a new restaurant to the collection 'restaurant' in database 'test'.
"""

import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
import json
from tkinter import ttk
import pymongo
import time
from datetime import datetime
from math import radians, cos, sin, asin, sqrt


"""----------------------------------------------------------------------------

This function is used to open a json file from your computer.
It will be called by the 'open'menu on the top part of window.
It will help you to import a .json file to the database named "test".
"""
#点击菜单栏“打开”后的动作函数
def openfile():
   file_in=tkinter.filedialog.askopenfile(title="打开一个Json文件",\
      filetypes=[("JSON",".json")])
   data=[]
   for line in file_in:
      dic = json.loads(line)
      data.append(dic)
   #date字段中有以$开头的部分，需要替换
   for item in data:
      """获取评分个数"""
      length=len(item['grades'])
      for i in range(0,length):
         #print(item['grades'][i])
         item['grades'][i]['date']['date']=\
            item['grades'][i]['date'].pop('$date')


   print("the json file has "+str(len(data))+" lines")
   """连接数据库"""
   #数据库名：test
   #集合名：restaurant
   myclient=pymongo.MongoClient('mongodb://localhost:27017/')
   dblist = myclient.list_database_names()
   if "test" in dblist:
      print("数据库存在！")
   print(dblist)
   mydb=myclient['test']
   collist = mydb.list_collection_names()
   if "restaurant" in collist: 
      print("restaurant集合存在！")
   mycol=mydb['restaurant']
   #先清空数据库
   x = mycol.delete_many({})
   print("数据库清空成功成功！")
   tkinter.messagebox.showinfo('提示 Notice',\
      'it will take 10 seconds,please wait！')
   mycol.insert_many(data)
   #for line in data:
      #mycol.insert_one(line)
   
   
   x = mycol.find_one()
   if x==data[0]:
      tkinter.messagebox.showinfo('提示 Notice','Success！')
   print(x)

"""----------------------------------------------------------------------------

This function is used to get the distance from Xi'an to restaurants
"""
def geodistance(lng1,lat1,lng2,lat2):
   #lng1,lat1,lng2,lat2 = (120.12802999999997,30.28708,115.86572000000001,28.7427)
   lng1, lat1, lng2, lat2 = \
      map(radians, [float(lng1), float(lat1), float(lng2), float(lat2)])
       # 经纬度转换成弧度
   dlon=lng2-lng1
   dlat=lat2-lat1
   a=sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
   distance=2*asin(sqrt(a))*6371*1000 # 地球平均半径，6371km
   distance=round(distance/1000,3)
   return distance

"""----------------------------------------------------------------------------

This function is used to search from database.
It will be called by the 'open'menu on the top part of window.
"""
#搜索按钮的动作函数
def search(name,borough,street,zipcode):
   """处理数据:首字母大写"""
   name=name.title()
   borough=borough.title()
   street=street.title()
   """处理数据:对字典进行过滤"""
   search_items={'name':name,'borough':borough,'street':street,\
      'zipcode':zipcode}
   print(search_items)
   
   search_items = {k: v for k, v in search_items.items() if v!=''}
   #去掉为空的搜索字段
   """构造语句"""
   if 'zipcode' in search_items.keys():
      #因为zipcode和street在内层，所以要把key字段替换成两层的形式
      search_items['address.zipcode']=search_items.pop('zipcode')
   if 'street' in search_items.keys():
      search_items['address.street']=search_items.pop('street')
   print(search_items)

   """连接数据库并查询"""
   myclient=pymongo.MongoClient('mongodb://localhost:27017/')
   dblist = myclient.list_database_names()
   if "test" in dblist:
      print("数据库存在！")
   print(dblist)
   mydb=myclient['test']
   collist = mydb.list_collection_names()
   if "restaurant" in collist: 
      print("restaurant集合存在！")
   mycol=mydb['restaurant']
   result=mycol.find(search_items)
   print(result)

   result_list=list(result)#格式化

   """从数据库返回的结构集中提取展示在主界面表格中的4个字段数据"""
   data_display=[]
   length=len(result_list)
   distance='none'
   for item in range(0,length):
      """构造单条展示数据，格式为一个List"""
      temp=[item+1,result_list[item]['name'],\
         result_list[item]['borough'],\
            result_list[item]['address']['street'],\
               result_list[item]['address']['zipcode'],distance]
      if result_list[item]['address']['coord']:
         x=result_list[item]['address']['coord'][0]
         y=result_list[item]['address']['coord'][1]
        
         distance=geodistance(x,y,34.16,108.54)
         distance=str(int(distance))+" KM"
         temp=[item+1,result_list[item]['name'],\
            result_list[item]['borough'],\
               result_list[item]['address']['street'],\
                  result_list[item]['address']['zipcode'],distance]
      data_display.append(temp)

   
   """用户可能进行多次搜索，在展示结果之前先清除旧数据"""
   length_data=len(data_display)
   x=data.get_children()#获取表格中的所有数据
   for item in x:
      data.delete(item)
   """把最新的数据展示在用户界面的表格中"""
   for i in range(0,length_data):
      data.insert('','end',values= data_display[i])
   tkinter.messagebox.showinfo("Result",\
      str(length_data)+" restautants found!")

"""----------------------------------------------------------------------------

This function is used to convert time stamp to the format we can read easily.
It will be called by the function named "details".
"""
def timeStamp(timeNum):
    timeStamp = float(timeNum/1000)
    timeArray = time.localtime(timeStamp)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime
"""----------------------------------------------------------------------------

This function is used to delete a restaurant in the window of details
of a restaurant.
"""
def delete_one(item_text1,item_text2,item_text3,item_text4):
   delete_item={'name':item_text1,'borough':item_text2,\
      'address.street':item_text3,'address.zipcode':item_text4}
   """连接数据库并查询"""
   myclient=pymongo.MongoClient('mongodb://localhost:27017/')
   dblist = myclient.list_database_names()
   if "test" in dblist:
      print("数据库存在！")
   mydb=myclient['test']
   collist = mydb.list_collection_names()
   if "restaurant" in collist: 
      print("restaurant集合存在！")
   mycol=mydb['restaurant']
   x=mycol.delete_one(delete_item)
   if(x.deleted_count==1):
      tkinter.messagebox.showinfo("Result","Deleted successfully!")

"""----------------------------------------------------------------------------

This function is used to show detail window when you double click a table line.
"""
def details(event):
   print('双击单元格')
   for item in data.selection():
      item_text = data.item(item,'value')
      print(item_text[0])#输出所选行的第一列的值
      print(item_text[1])
   """构造查询条件"""
   search_items={'name':item_text[1],'borough':item_text[2],\
      'address.street':item_text[3],'address.zipcode':item_text[4]}
   print(search_items)
   """连接数据库并查询"""
   myclient=pymongo.MongoClient('mongodb://localhost:27017/')
   dblist = myclient.list_database_names()
   if "test" in dblist:
      print("数据库存在！")
   print(dblist)
   mydb=myclient['test']
   collist = mydb.list_collection_names()
   if "restaurant" in collist: 
      print("restaurant集合存在！")
   mycol=mydb['restaurant']
   result=mycol.find(search_items)
   print(result)

   result_list=list(result)
   print(result_list)

   """显示窗口"""
   detail_window=tk.Tk()
   detail_window.title("餐厅详细信息 The details of restaurant you selected")
   detail_window.geometry('900x500')
   tk.Label(detail_window,text='Details of Restaurant',\
      font=("微软雅黑", 16)).grid(row=0,column=0,pady=5,padx=10)

   tk.Label(detail_window,text='餐厅名 Restaurant name',\
      font=("微软雅黑", 12)).grid(row=1,column=0)
   tk.Label(detail_window,text=result_list[0]['name'],\
      font=("微软雅黑", 12)).grid(row=1,column=1)
   tk.Label(detail_window,text='餐厅ID',\
      font=("微软雅黑", 12)).grid(row=2,column=0)
   tk.Label(detail_window,text=result_list[0]['restaurant_id'],\
      font=("微软雅黑", 12)).grid(row=2,column=1)
   tk.Label(detail_window,text='所在地/自治市 Borough',\
      font=("微软雅黑", 12)).grid(row=3,column=0)
   tk.Label(detail_window,text=result_list[0]['borough'],\
      font=("微软雅黑", 12)).grid(row=3,column=1)
   tk.Label(detail_window,text='坐标 Coord',\
      font=("微软雅黑", 12)).grid(row=4,column=0)
   tk.Label(detail_window,text=result_list[0]['address']['coord'][0],\
      font=("微软雅黑", 12)).grid(row=4,column=1)
   tk.Label(detail_window,text=result_list[0]['address']['coord'][1],\
      font=("微软雅黑", 12)).grid(row=4,column=2)
   tk.Label(detail_window,text='街道 Street',\
      font=("微软雅黑", 12)).grid(row=5,column=0)
   tk.Label(detail_window,text=result_list[0]['address']['street'],\
      font=("微软雅黑", 12)).grid(row=5,column=1)
   tk.Label(detail_window,text='建筑号 Building number',\
      font=("微软雅黑", 12)).grid(row=6,column=0)
   tk.Label(detail_window,text=result_list[0]['address']['building'],\
      font=("微软雅黑", 12)).grid(row=6,column=1)
   tk.Label(detail_window,text='邮政编码 Zipcode',\
      font=("微软雅黑", 12)).grid(row=7,column=0)
   tk.Label(detail_window,text=result_list[0]['address']['zipcode'],\
      font=("微软雅黑", 12)).grid(row=7,column=1)
   tk.Label(detail_window,text='主菜 Cuisine',\
      font=("微软雅黑", 12)).grid(row=8,column=0)
   tk.Label(detail_window,text=result_list[0]['cuisine'],\
      font=("微软雅黑", 12)).grid(row=8,column=1)
   
   tk.Label(detail_window,text='Marks',\
      font=("微软雅黑", 16)).grid(row=9,column=0,pady=5,padx=5)
   lenth_of_grades=len(result_list[0]['grades'])
   for i in range(0,lenth_of_grades):
      tk.Label(detail_window,text='评分 Mark'+str(i+1),\
         font=("微软雅黑", 12)).grid(row=10+i,column=0)
      tk.Label(detail_window,text=' 评定日期 Date',font=("微软雅黑", 12),\
         bg='#6699CC',fg='white').grid(row=10+i,column=1)
      tk.Label(detail_window,\
         text=timeStamp(result_list[0]['grades'][i]['date']['date']),\
         font=("微软雅黑", 12),bg='white').grid(row=10+i,column=2)
      tk.Label(detail_window,text=' 评定等级 Grade',font=("微软雅黑", 12),\
         bg='#6699CC',fg='white').grid(row=10+i,column=3)
      tk.Label(detail_window,text=result_list[0]['grades'][i]['grade'],\
         font=("微软雅黑", 12),bg='white').grid(row=10+i,column=4)
      tk.Label(detail_window,text=' 得分 Score',font=("微软雅黑", 12),\
         bg='#6699CC',fg='white').grid(row=10+i,column=5)
      tk.Label(detail_window,text=result_list[0]['grades'][i]['score'],\
         font=("微软雅黑", 12),bg='white').grid(row=10+i,column=6)

   delete_button=tk.Button(detail_window,text='删除(Delete)',bg='#CC0033',\
   fg='white',command=\
      lambda : delete_one(item_text[1],item_text[2],\
         item_text[3],item_text[4]))
   delete_button.grid(row=18,column=1)
   

   detail_window.mainloop()

"""----------------------------------------------------------------------------

This function is used to search from database.
It will be called by the 'open'menu on the top part of window.
"""
def save_new(
   e_name,e_borough,e_coord_x,e_id,\
      e_coord_y,e_street,e_zipcode,e_cuisine,e_building
):

   #构造数据
   new_data={ 
   "address": 
   { 
      "building": e_building.title(), 
      "coord": [e_coord_x, e_coord_y], 
      "street": e_street.title(), 
      "zipcode": e_zipcode
   }, 
   "borough": e_borough.title(), 
   "cuisine": e_cuisine.title(), 
   "grades": 
   [ 
     
   ], 
    "name": e_name.title(), 
   "restaurant_id": e_id.title() 
   }

   #连接数据库
   myclient=pymongo.MongoClient('mongodb://localhost:27017/')
   dblist = myclient.list_database_names()
   if "test" in dblist:
      print("数据库存在！")
   print(dblist)
   mydb=myclient['test']
   collist = mydb.list_collection_names()
   if "restaurant" in collist: 
      print("restaurant集合存在！")
   mycol=mydb['restaurant']
   #插入数据
   x=mycol.insert_one(new_data)
   inserted_id=x.inserted_id
   #判断是否插入成功
   find=mycol.find({"_id":inserted_id},{"_id": 0, "restaurant_id": 1})
   find=list(find)
   print(find)
   if(new_data['restaurant_id']==find[0]['restaurant_id']):
      tkinter.messagebox.showinfo('提示','添加成功！Success!')
   else:
      tkinter.messagebox.showerror\
         ('错误','对不起，添加失败，请检查后重试！Failed!')

"""----------------------------------------------------------------------------

This function is used to add a new restaurant.
It will be called by the 'new'menu on the top part of window.
It will call a sub-window which is used to collect information of restayrant.
"""
def new_restaurant():
   new_window=tk.Toplevel()
   new_window.title("新建餐厅(New restaurant)")
   new_window.geometry('700x350')

   tk.Label(new_window,text='Information',\
      font=("微软雅黑", 16)).grid(row=0,column=0,pady=5,padx=10)

   e_name = tk.StringVar()
   e_id = tk.StringVar()
   e_borough = tk.StringVar()
   e_coord_x = tk.DoubleVar()
   e_coord_y = tk.DoubleVar()
   e_street=tk.StringVar()
   e_building=tk.StringVar()
   e_zipcode=tk.StringVar()
   e_cuisine=tk.StringVar()

   tk.Label(new_window,text='餐厅名 Name',\
      font=("微软雅黑", 12)).grid(row=1,column=0)
   tk.Entry(new_window,textvariable = e_name,\
      font=("微软雅黑", 12)).grid(row=1,column=1,columnspan=2)

   tk.Label(new_window,text='餐厅ID',\
      font=("微软雅黑", 12)).grid(row=2,column=0)
   tk.Entry(new_window,font=("微软雅黑", 12),\
      textvariable =e_id).grid(row=2,column=1,columnspan=2)

   tk.Label(new_window,text='所在地/自治市 Borough',\
      font=("微软雅黑", 12)).grid(row=3,column=0)
   tk.Entry(new_window,font=("微软雅黑", 12),\
      textvariable=e_borough).grid(row=3,column=1,columnspan=2)

   tk.Label(new_window,text='坐标',\
      font=("微软雅黑", 12)).grid(row=4,column=0)
   tk.Label(new_window,text=' X坐标',\
      font=("微软雅黑", 12)).grid(row=4,column=1)
   tk.Entry(new_window,font=("微软雅黑", 12),\
      textvariable =e_coord_x,width=5).grid(row=4,column=2)
   tk.Label(new_window,text=' Y坐标',\
      font=("微软雅黑", 12)).grid(row=4,column=3)
   tk.Entry(new_window,font=("微软雅黑", 12),\
      textvariable =e_coord_y,width=5).grid(row=4,column=4)

   tk.Label(new_window,text='街道 Street',\
      font=("微软雅黑", 12)).grid(row=5,column=0)
   tk.Entry(new_window,font=("微软雅黑", 12),\
      textvariable =e_street).grid(row=5,column=1,columnspan=2)

   tk.Label(new_window,text='建筑号 Building id',\
      font=("微软雅黑", 12)).grid(row=6,column=0)
   tk.Entry(new_window,font=("微软雅黑", 12),\
      textvariable =e_building).grid(row=6,column=1,columnspan=2)

   tk.Label(new_window,text='邮政编码 Zipcode',\
      font=("微软雅黑", 12)).grid(row=7,column=0)
   tk.Entry(new_window,font=("微软雅黑", 12),\
      textvariable =e_zipcode).grid(row=7,column=1,columnspan=2)

   tk.Label(new_window,text='主菜 Cuisine',\
      font=("微软雅黑", 12)).grid(row=8,column=0)
   tk.Entry(new_window,font=("微软雅黑", 12),\
      textvariable =e_cuisine).grid(row=8,column=1,columnspan=2)
   

   

   """保存按钮"""
   save_button=tk.Button(new_window,text='保存(Save)',bg='#009966'\
   ,fg='white',command=lambda : save_new(e_name.get(),e_borough.get(),\
      e_coord_x.get(),e_id.get(),\
      e_coord_y.get(),e_street.get(),e_zipcode.get(),\
      e_cuisine.get(),e_building.get()))
   save_button.grid(row=17,column=1)

   new_window.mainloop()

"""----------------------------------------------------------------------------

This function is used to sort the data by the distance.
"""
def treeview_sort_column(tv, col, reverse):  # Treeview、列名、排列方式
   li = []
   tkinter.messagebox.showinfo('提示 Notice',\
      'it will take 10 seconds,please wait！')
   for k in tv.get_children(''):
      if tv.set(k, col)[:-2] != 'no':
         li.append((float(tv.set(k, col)[:-2]), k))
   li.sort(reverse=reverse)  # 排序方式
   # rearrange items in sorted positions
   for index, (val, k) in enumerate(li):  # 根据排序后索引移动
      tv.move(k, '', index)
   # 重写标题，使之成为再点倒序的标题
   tv.heading(col, command=lambda: \
      treeview_sort_column(tv, col, not reverse))
"""----------------------------------------------------------------------------

This part is the main part of this program which calls the main window.
"""

#主窗口
window = tk.Tk()
window.title("Restauraants Management System")
window.geometry('1000x500')
width=window.winfo_width()
height=window.winfo_height()
#主框架
frame = tk.Frame(window)
frame.pack()

#内部框架
#菜单栏
frame_menu = tk.Frame(frame)
#其余部分
frame_main = tk.Frame(frame)
frame_menu.pack(side='top')
frame_main.pack(side='bottom')
#其余部分左右分栏
frame_left = tk.Frame(frame_main,height=300)
frame_right = tk.Frame(frame_main,height=500)
frame_left.pack(side='left', expand='no', anchor='w',\
    fill='y', padx=5, pady=5)
frame_right.pack(side='top',fill='x')


#创建菜单
menubar = tk.Menu(frame_menu)
openmenu = tk.Menu(menubar,tearoff=0)
menubar.add_cascade(label='打开(Open)',menu=openmenu)
openmenu.add_command(label="import json",command=openfile)

newmenu = tk.Menu(menubar,tearoff=0)
menubar.add_cascade(label='新建(New)',menu=newmenu)
newmenu.add_command(label="new restaurant",command=new_restaurant)

#aboutmenu = tk.Menu(menubar,tearoff=0)
#menubar.add_cascade(label='关于(About)',menu=aboutmenu)
window.config(menu=menubar)

#左边栏
left_label=tk.Label(frame_left,text="搜索选项（Search option）",\
   bg='lightgrey',width=30,height=2,font = "微软雅黑 10 bold")
left_label.pack()
"""搜索变量"""
name=tk.StringVar()
borough=tk.StringVar()
street=tk.StringVar()
zipcode=tk.StringVar()
"""搜索框"""

entry_name=tk.Entry(frame_left,textvariable=name,font=('Arial',14))
entry_borough=tk.Entry(frame_left,textvariable=borough,font=('Arial',14))
entry_street=tk.Entry(frame_left,textvariable=street,font=('Arial',14))
entry_zipcode=tk.Entry(frame_left,textvariable=zipcode,font=('Arial',14))
tk.Label(frame_left,text="Name",anchor = 'w').pack()
entry_name.pack()
tk.Label(frame_left,text="Borough").pack()
entry_borough.pack()
tk.Label(frame_left,text="Street").pack()
entry_street.pack()
tk.Label(frame_left,text="Zipcode").pack()
entry_zipcode.pack()
"""搜索按钮"""
search_button=tk.Button(frame_left,bg='#009966',fg='white',text='搜索(Search)',\
command=lambda : search(name.get(),borough.get(),street.get(),zipcode.get()))
search_button.pack()
"""提示"""
tk.Label(frame_left,text="Tips",height=2,font = "微软雅黑 10 bold").pack()
tk.Label(frame_left,text="Click search button to show all.").pack()
tk.Label(frame_left,text="Double click to view the details.").pack()
tk.Label(frame_left,text="Click the heading of distance can sort.").pack()
#右边栏
right_top=tk.Frame(frame_right)
right_middle=tk.Frame(frame_right)

right_top.pack(side='top')
right_middle.pack(side='top')

"""标题"""
tk.Label(right_top,text="搜索结果(Search Result)",bg="lightgrey",\
   width=100,height=2,font = "微软雅黑 10 bold").pack(anchor='nw',pady=5)
"""表格"""
data=ttk.Treeview(right_middle,show="headings",height=20)
data['columns']=['','name','borough','street','zipcode','distance']

# 加滚条
S = tk.Scrollbar(right_middle,orient=tk.VERTICAL, command=data.yview)
data.configure(yscrollcommand=S.set)
data.pack(side=tk.LEFT)
S.pack(side=tk.LEFT, fill=tk.Y)

"""设置列宽度"""
data.column('',width=50)
data.column('name',width=140)
data.column('borough',width=140)
data.column('street',width=140)
data.column('zipcode',width=120)
data.column('distance',width=120)
"""设置列名"""
data.heading('name',text='名字 Name')
data.heading('borough',text='自治市区 Borough')
data.heading('street',text='街道 Street')
data.heading('zipcode',text='邮政编码 Zipcode')
data.heading('distance',text='距离 Distance',\
   command=lambda: treeview_sort_column(data, "distance", False))
"""数据行绑定事件"""
data.bind('<Double-1>', details)




#主窗口循环显示
window.mainloop()
