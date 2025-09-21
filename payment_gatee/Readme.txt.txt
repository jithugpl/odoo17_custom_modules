**Tested Version**

Installation steps:
1-	Before adding the plug-in to your Odoo website you should restart Odoo server to make sure there is no errors in your server (using terminal by typing “sudo systemctl restart odoo16”).
2-	After downloading the plug-in you should move it to your Odoo addon directory.
Default directory: “Odoo/server/odoo/addons”.
3-	You should restart Odoo server using terminal by typing “sudo systemctl restart odoo16”
4-	Go to you Odoo website and login with admin user.
5-	Then from setting/General settings active debug mode.
6-	Go to apps and click update apps list and confirm it.
7-	Click on update.
8-	Search for “payment_gatee”.
9-	Click install on it.
10-	Go to invoicing.
11-	Go to configuration tap then payment provider.
12-	Search for “payment_gatee” and click on it
13-	You will have edit button in top left click on it.
14-	Change the state to enabled.
15-	In credentials tab add your Gate-E unique id and hash.
16-	Select your wanted API type.
17-	In show callback if you want customer see Gate-E call back and 0 if you don’t want.
18-	In locale enter “en” for English and “ar” for Arabic.
19-	Change payment journal to bank.
20-	Click save and the payment gateway will be added to checkout page.
