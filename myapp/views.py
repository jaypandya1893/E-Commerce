from django.shortcuts import render,redirect
from . models import User,Product,Wishlist,Cart,Transaction
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .paytm import generate_checksum, verify_checksum
import requests
# from django.conf import settings
# from django.core.mail import send_mail
# import rendom
# Create your views here.


def initiate_payment(request):
	user=User.objects.get(email=request.session['email'])
	try: 
	    amount = int(request.POST['amount'])
	except:
   		render(request, 'cart.html', context={'error': 'Wrong Accound Details or amount'})
	transaction = Transaction.objects.create(made_by=user, amount=amount)
	transaction.save()
	merchant_key = settings.PAYTM_SECRET_KEY

	params = (
	      ('MID', settings.PAYTM_MERCHANT_ID),
	      ('ORDER_ID', str(transaction.order_id)),
	      ('CUST_ID', str(transaction.made_by.email)),
	      ('TXN_AMOUNT', str(transaction.amount)),
	      ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
            ('WEBSITE', settings.PAYTM_WEBSITE),
	    # ('EMAIL', request.user.email),
	    # ('MOBILE_N0', '9911223388'),
            ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
            ('CALLBACK_URL', 'http://localhost:8000/callback/'),
          # ('PAYMENT_MODE_ONLY', 'NO'),
		)

	paytm_params = dict(params)
	checksum = generate_checksum(paytm_params, merchant_key)

	transaction.checksum = checksum
	transaction.save()

	carts=Cart.objects.filter(user=User,payment_status=False)
	for i in carts:
	    i.payment_status=True
	    i.save()
	carts=Cart.objects.filter(user=User,payment_status=False)
	request.session['cart_count']=len(carts)	
	paytm_params['CHECKSUMHASH'] = checksum
	print('SENT: ', checksum)
	return render(request, 'redirect.html', context=paytm_params)

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        received_data = dict(request.POST)
        paytm_params = {}
        paytm_checksum = received_data['CHECKSUMHASH'][0]
        for key, value in received_data.items():
            if key == 'CHECKSUMHASH':
                paytm_checksum = value[0]
            else:
                paytm_params[key] = str(value[0])
        # Verify checksum
        is_valid_checksum = verify_checksum(paytm_params, settings.PAYTM_SECRET_KEY, str(paytm_checksum))
        if is_valid_checksum:
            received_data['message'] = "Checksum Matched"
        else:
            received_data['message'] = "Checksum Mismatched"
            return render(request, 'callback.html', context=received_data)
        return render(request, 'callback.html', context=received_data)

def  index(request):
	try:
		user=User.objects.get(email=request.session['email'])
		if user.usertype=='buyer':
			return render(request,'index.html')
		else:
			return render(request,'sellerindex.html')
	except:
		return render(request,'index.html')

def  sellerindex(request):
	return render(request,'sellerindex.html')

def  shop(request):
	products=Product.objects.all()
	products500=Product.objects.filter(product_price__range=(0,500))
	products1000=Product.objects.filter(product_price__range=(501,1000))
	products1001=Product.objects.filter(product_price__range=(1001,10000))
	return render(request,'shop.html',{'products':products,'products500':products500,'products1000':products1000,'products1001':products1001})

def  products500(request):
	products=Product.objects.filter(product_price__range=(0,500))
	products500=Product.objects.filter(product_price__range=(0,500))
	products1000=Product.objects.filter(product_price__range=(501,1000))
	products1001=Product.objects.filter(product_price__range=(1001,10000))
	return render(request,'shop.html',{'products':products,'products500':products500,'products1000':products1000,'products1001':products1001})

def  products1000(request):
	products=Product.objects.filter(product_price__range=(501,1000))
	products500=Product.objects.filter(product_price__range=(0,500))
	products1000=Product.objects.filter(product_price__range=(501,1000))
	products1001=Product.objects.filter(product_price__range=(1001,10000))
	return render(request,'shop.html',{'products':products,'products500':products500,'products1000':products1000,'products1001':products1001})

def  products1001(request):
	products=Product.objects.filter(product_price__range=(1001,10000))
	products500=Product.objects.filter(product_price__range=(0,500))
	products1000=Product.objects.filter(product_price__range=(501,1000))
	products1001=Product.objects.filter(product_price__range=(1001,10000))
	return render(request,'shop.html',{'products':products,'products500':products500,'products1000':products1000,'products1001':products1001})

def  detail(request,pk):
	wishlist_flag=False
	cart_flag=False
	path=request.get_full_path()
	product=Product.objects.get(pk=pk)
	try:
		user=User.objects.get(email=request.session['email'])
		Wishlist.objects.get(user=user,product=product)
		wishlist_flag=True
	except:
		pass
	try:
		user=User.objects.get(email=request.session['email'])
		Cart.objects.get(user=user,product=product,payment_status=False)
		cart_flag=True
	except:
		pass
	return render(request,'detail.html',{'product':product,'path':path,'wishlist_flag':wishlist_flag,'cart_flag':cart_flag})

def  checkout(request):
	return render(request,'checkout.html')

def  contact(request):
	return render(request,'contact.html')

def  login(request):
	if request.method=="POST":
		path=request.POST['path']
		try:
			user=User.objects.get(email=request.POST['email'])
			if user.password==request.POST['password']:
				if user.usertype=="buyer":
					request.session['fname']=user.fname
					request.session['email']=user.email
					request.session['profilepic']=user.profilepic.url
					wishlists=Wishlist.objects.filter(user=user)
					request.session['wishlist_count']=len(wishlists)
					carts=Cart.objects.filter(user=user,payment_status=False)
					request.session['cart_count']=len(carts)
					url = "https://www.fast2sms.com/dev/bulkV2"
					# otp=random.randint(1000,9999)
					# querystring = {"authorization":"YOUR_API_KEY","message": "You Have Loggedin Successfully","language": "english","variables_values":str(otp)"route":"otp","numbers":"9408747609"}
					# headers = {
    				# 			'cache-control': "no-cache"
					# 			}
					# response = requests.request("GET", url, headers=headers, params=querystring)
					# print(response.text)
					if path==None:
						return redirect(path)
					else:	
						return render(request,'index.html')
				else:
					request.session['fname']=user.fname
					request.session['email']=user.email
					request.session['profilepic']=user.profilepic.url
					return render(request,'sellerindex.html')
			else:
				msg="Incorrect Password"
				return render(request,'login.html',{'msg':msg})
		except:
			msg="Email Not Register"
			return render(request,'login.html',{'msg':msg})

	else:
		path=request.GET.get('path')
		return render(request,'login.html',{'path':path})

def  register(request):
	if request.method=="POST":
		try:
			user=User.objects.get(email=request.POST['email'])
			msg="Email Already Register"
			return render(request,'register.html',{'msg':msg})
		except:
			if request.POST['password']==request.POST['cpassword']:
				User.objects.create(
					usertype=request.POST['usertype'],
					fname=request.POST['fname'],
					lname=request.POST['lname'],
					email=request.POST['email'],
					mobile=request.POST['mobile'],
					address=request.POST['address'],
					password=request.POST['password'],
					profilepic=request.FILES['profilepic'],
    				)
				msg="User Register Successfully"
				return render(request,'login.html',{'msg':msg})
			else:
				msg="Password and Confirm Password Does Not Match"
				return render(request,'register.html',{'msg':msg})
	else:
		return render(request,'register.html')

def  logout(request):
	try:
		del request.session['email']
		del request.session['fname']
		del request.session['profilepic']
		del request.session['wishlist_count']
		del request.session['cart_count']
		msg="User Logged Out"
		return render(request,'login.html',{'msg':msg})
	except:
		return render(request,'login.html')

def changepassword(request):
	if request.method=="POST":
		user=User.objects.get(email=request.session['email'])
		if user.password==request.POST['oldpassword']:
			if request.POST['newpassword']==request.POST['cnewpassword']:
				user.password=request.POST['newpassword']
				user.save()
				return redirect('logout')
			else:
				msg="New Password & Confirm New Password Does Not Match"
				return render(request,'changepassword.html',{'msg':msg})
		else:
			msg="Old Password Does Not Match"
			return render(request,'changepassword.html',{'msg':msg})
	else:
		return render(request,'changepassword.html')

def sellerchangepassword(request):
	if request.method=="POST":
		user=User.objects.get(email=request.session['email'])
		if user.password==request.POST['oldpassword']:
			if request.POST['newpassword']==request.POST['cnewpassword']:
				user.password=request.POST['newpassword']
				user.save()
				return redirect('logout')
			else:
				msg="New Password & Confirm New Password Does Not Match"
				return render(request,'sellerchangepassword.html',{'msg':msg})
		else:
			msg="Old Password Does Not Match"
			return render(request,'sellerchangepassword.html',{'msg':msg})
	else:
		return render(request,'sellerchangepassword.html')

def  selleraddproduct(request):
	seller=User.objects.get(email=request.session['email'])
	if request.method=="POST":
		Product.objects.create(
				seller=seller,
				product_name=request.POST['product_name'],
				product_category=request.POST['product_category'],
				product_price=request.POST['product_price'],
				product_desc=request.POST['product_desc'],
				product_size=request.POST['product_size'],
				product_image=request.FILES['product_image'],
		)
		msg="Product Add Successfully"
		return render(request,'selleraddproduct.html',{'msg':msg})
	else:
		return render(request,'selleraddproduct.html')

def  sellerviewproduct(request):
	seller=User.objects.get(email=request.session['email'])
	products=Product.objects.filter(seller=seller)
	return render(request,'sellerviewproduct.html',{'products':products})

def sellerproductdetail(request,pk):
	product=Product.objects.get(pk=pk)
	return render(request,'sellerproductdetail.html',{'product':product})

def sellereditproduct(request,pk):
	product=Product.objects.get(pk=pk)
	if request.method=="POST":
		product.product_category=request.POST['product_category']
		product.product_name=request.POST['product_name']
		product.product_price=request.POST['product_price']
		product.product_desc=request.POST['product_desc']
		product.product_size=request.POST['product_size']
		try:
			product.product_image=request.FILES['product_image']
		except:
			pass
		product.save()
		msg="Product Updated Successfully"
		return render(request,'sellereditproduct.html',{'product':product,'msg':msg})
	else:
		return render(request,'sellereditproduct.html',{'product':product})
def sellerdeleteproduct(request,pk):
	product=Product.objects.get(pk=pk)
	product.delete()
	return redirect('sellerviewproduct')

def addtowishlist(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	Wishlist.objects.create(user=user,product=product)
	return redirect('wishlist')

def wishlist(request):
	user=User.objects.get(email=request.session['email'])
	wishlists=Wishlist.objects.filter(user=user)
	request.session['wishlist_count']=len(wishlists)
	return render(request,'wishlist.html',{'wishlists':wishlists})

def removefromwishlist(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	wishlist=Wishlist.objects.get(user=user,product=product)
	wishlist.delete()
	return redirect('wishlist')

def addtocart(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	Cart.objects.create(user=user,product=product,product_price=product.product_price,product_qty=1,total_price=product.product_price)
	return redirect('cart')

def cart(request):
	net_price=0
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,payment_status=False)
	for i in carts:
		net_price=net_price+i.total_price
	request.session['cart_count']=len(carts)
	return render(request,'cart.html',{'carts':carts,'net_price':net_price})

def removefromcart(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	cart=Cart.objects.get(user=user,product=product)
	cart.delete()
	return redirect('cart')

def change_qty(request):
	cid=int(request.POST['cid'])
	cart=Carts.objects.get(pk=cid)
	product_price=cart.product.product_price
	product_qty=int(request.POST['product_qty'])
	total_price=product_price*product_qty
	cart.product_qty=product_qty
	cart.total_price=total_price
	cart.save()
	return redirect('cart')

def search(request):
	search=request.POST['search']
	products=Product.objects.filter(product_name__contains=search)
	return render(request,'search.html',{'products':products})

def myorder(request):
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,payment_status=False)
	return render(request,'myorder.html',{'carts':carts})

# def email(request):

#     subject = 'OTP For Forgot Password'
      # otp=rendom.randint(1000,9999)
#     message = ' Hello User, Your OTP For Forgot Password Is:'+str(otp)
#     email_from = settings.EMAIL_HOST_USER
#     recipient_list = ['receiver@gmail.com',]
#     send_mail( subject, message, email_from, recipient_list )
#     return redirect('redirect to a new page')