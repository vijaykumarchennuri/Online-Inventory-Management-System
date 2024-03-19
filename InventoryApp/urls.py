from django.urls import path

from . import views

urlpatterns = [path("index.html", views.index, name="index"),
	       path('Login.html', views.Login, name="Login"), 
	       path('Register.html', views.Register, name="Register"),
	       path('Signup', views.Signup, name="Signup"),
	       path('UserLogin', views.UserLogin, name="UserLogin"),	   
	       path('PurchaseProduct', views.PurchaseProduct, name="PurchaseProduct"),
	       path('Purchase', views.Purchase, name="Purchase"),
	       path('SaleProductAction', views.SaleProductAction, name="SaleProductAction"),
	       path('PaymentAction', views.PaymentAction, name="PaymentAction"),
	       path('ViewTransactions', views.ViewTransactions, name="ViewTransactions"),
	       path('ViewUsers', views.ViewUsers, name="ViewUsers"),
	       path('PredictStock.html', views.PredictStock, name="PredictStock"), 
	        path('PredictStockAction.html', views.PredictStockAction, name="PredictStockAction"), 
]