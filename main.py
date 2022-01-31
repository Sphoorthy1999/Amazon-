import json
import os

from flask import Flask
from flask import request
from flask import Response
import mysql.connector
import uuid

a = Flask("Amazon")
connection = mysql.connector.connect(host='localhost',database="amazon",user='root',password='Sphoorthy@99',autocommit=True)

@a.route("/register",methods=["POST"])
def register():
    cursor=connection.cursor(dictionary=True)
    b=request.json
    try:
        cursor.execute(f"insert into amazon.users (username,passwd,contact,email) values ('{b['username']}','{b['passwd']}',{b['contact']},'{b['email']}')")
        cursor.execute(f"select * from amazon.users where {'contact'} = {b['contact']}")
        z=cursor.fetchall()
        return Response(json.dumps({"message": "Registered successfully", "data": z}), 200)
    except Exception as e:
        return Response(str(e),400)


@a.route("/login",methods=["POST"])
def login():
    cursor = connection.cursor(dictionary=True)
    b=request.json
    try:
        cursor.execute(f"select * from amazon.users where {'contact'} = {b['contact']} and {'passwd'} = '{b['passwd']}'")
        z=cursor.fetchall()
        if z:
            return Response(json.dumps({"message": "Login successful", "data": z}), 200)
        else:
            return Response(json.dumps({"message": "Contact & password not matched. Please register!!!"}), 400)
    except Exception as e:
        return Response(str(e),400)


@a.route("/addproduct",methods=["POST"])
def addproduct():
    cursor = connection.cursor(dictionary=True)
    b=request.json
    try:
        cursor.execute(f"insert into amazon.products (productname,model,price,stock) values ('{b['productname']}','{b['model']}',{b['price']},{b['stock']}) ")
        cursor.execute(f"select * from amazon.products where {'productname'} = '{b['productname']}' and {'model'} = '{b['model']}'")
        z=cursor.fetchall()
        return Response(json.dumps({"message": "Product added successfully", "data": z}), 200)
    except Exception as e:
        return Response(str(e),400)


@a.route("/productlist",methods=["GET"])
def productlist():
    print("hello")
    return
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("select * from amazon.products")
        z=cursor.fetchall()
        return Response(json.dumps({"message": "Product list fetched successfully", "data": z}), 200)
    except Exception as e:
        return Response(str(e),400)

@a.route("/addcoupon",methods=["POST"])
def addcoupon():
    cursor = connection.cursor(dictionary=True)
    b=request.json
    try:
        cursor.execute(f"insert into amazon.coupons (discount,couponcode) values ({b['discount']},'{b['couponcode']}')")
        cursor.execute(f"select * from amazon.coupons where {'couponcode'} = '{b['couponcode']}'")
        z = cursor.fetchall()
        return Response(json.dumps({"message": "Coupon added successfully", "data": z}), 200)
    except Exception as e:
        return Response(str(e), 400)

@a.route("/updatecoupon",methods=["POST"])
def updatecoupon():
    cursor = connection.cursor(dictionary=True)
    b=request.json
    try:
        k=map(lambda x:f"{(b['couponid'],x)}",b["addprolist"])
        # for id in b["addprolist"]:
        #     k.append(f"{(b['couponid'],id)}")
        if b["addprolist"]:
            cursor.execute(f"insert into amazon.coupon_product (couponid,productid) values {','.join(k)}")
        l=[x for x in b["removeprolist"]]
        # for id in b["removeprolist"]:
        #     l.append(id)
        if b["removeprolist"]:
            cursor.execute(f"delete from amazon.coupon_product where {'couponid'} = {b['couponid']} and {'productid'} in {tuple(l)}")
        cursor.execute("select * from amazon.coupon_product")
        z=cursor.fetchall()
        return Response(json.dumps({"message": "Coupon added successfully", "data": z}), 200)
    except Exception as e:
        return Response(str(e), 400)

@a.route("/coupon",methods=["GET"])
def productcoupons():
    cursor = connection.cursor(dictionary=True)
    b=request.args
    try:
        cursor.execute(f"select * from amazon.coupon_product inner join amazon.coupons on {'amazon.coupon_product.couponid'} = {'amazon.coupons.id'} where {'amazon.coupon_product.productid'} = {b['productid']}")
        z=cursor.fetchall()
        if not z:
            return Response(json.dumps("No coupons for the selected product"), 400)
        else:
            return Response(json.dumps({"message": "Fetched coupon list", "data": z}), 200)
    except Exception as e:
        return Response(str(e), 400)

@a.route("/addtocart",methods=["POST"])
def addtocart():
    cursor = connection.cursor(dictionary=True)
    b=request.json
    try:
        cursor.execute(f"select ifnull(sum(totalcount),0) as totalcount from amazon.cart where {'productid'} = {b['productid']} and {'userid'} = {b['userid']}")
        z=cursor.fetchall()
        cursor.execute(f"select * from products where {'id'} = {b['productid']}")
        k=cursor.fetchall()
        b['totalcount']=b['totalcount'] + z[0]['totalcount']
        if b['totalcount']<= k[0]['stock']:
            cursor.execute(f"replace into amazon.cart (userid,productid,totalcount) values({b['userid']},{b['productid']},{b['totalcount']})")
            return Response(json.dumps({"message": "Added to cart successfully"}), 200)
        else:
            return Response(json.dumps({"message": "stock less than your requirement for this product"}), 400)
    except Exception as e:
        return Response(str(e), 400)


@a.route("/cart/id",methods=["GET"])
def cart():
    cursor = connection.cursor(dictionary=True)
    b=request.json
    try:
        cursor.execute(f"select * from amazon.cart inner join amazon.products on {'amazon.cart.productid'} = {'amazon.products.id'} where {'amazon.cart.userid'} = {b['userid']}")
        z=cursor.fetchall()
        if z:
            return Response(json.dumps(({"message": "Fetched items in the cart successfully", "data": z})), 200)
        else:
            return Response(json.dumps("No items in the cart"), 200)
    except Exception as e:
        return Response(str(e), 400)

@a.route("/applycoupon",methods=["POST"])
def applycoupon():
    cursor = connection.cursor(dictionary=True)
    b=request.json
    try:
        cursor.execute(f"update amazon.cart set couponid = {b['couponid']} where {'productid'} = {b['productid']} and {'userid'} = {b['userid']}")
        cursor.execute(f"select * from amazon.cart where {'productid'} = {b['productid']} and {'userid'} = {b['userid']}")
        z=cursor.fetchall()
        return Response(json.dumps({"message": "Coupon applied successfully", "data": z}), 200)
    except Exception as e:
        return Response(str(e), 400)

@a.route("/bill",methods=["GET"])
def bill():
    cursor = connection.cursor(dictionary=True)
    bill=0
    b=request.args
    try:
        cursor.execute(f"select ifnull(couponid,0) as couponid,totalcount,productid from amazon.cart where {'userid'} = {b['userid']}")
        z=cursor.fetchall()
        for x in z:
            cursor.execute(f"update amazon.products set {'stock'} = {'stock'}-{x['totalcount']} where {'id'} = {x['productid']}")
            if x['couponid'] == 0:
                cursor.execute(f"select {'price'}*{'totalcount'} as bill from amazon.cart inner join amazon.products on {'amazon.cart.productid'} = {'amazon.products.id'} where {'amazon.cart.userid'}= {b['userid']} and {'amazon.cart.couponid'}  IS NULL ")
                l=cursor.fetchone()
                bill+=l['bill']
                print(bill)
            else:
                cursor.execute(f"select {'price'}*{'totalcount'}*{'discount'}*{0.01} as bill from amazon.cart inner join amazon.products on {'amazon.cart.productid'} = {'amazon.products.id'} inner join amazon.coupons on {'amazon.cart.couponid'} = {'amazon.coupons.id'}  where {'amazon.cart.userid'}= {b['userid']} and {'couponid'} = {x['couponid']}")
                l=cursor.fetchone()
                bill+=l['bill']
                print(bill)
        cursor.execute(f"delete from amazon.cart where {'userid'}= {b['userid']}")
        return Response(json.dumps({"message": "Fetched bill successfully","data": float(bill)}), 200)
    except Exception as e:
        return Response(str(e), 400)

a.run(host="0.0.0.0",port=5556)