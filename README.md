# Auction site built with Django + Bootstrap

models.py contains model that stores the different kinds of data

views.py provides the web page the data it wants to show and some process behind it

urls.py links the web page and views.py

use django admin at http://127.0.0.1:8000/admin/ to add, delete, edit the internal data

# Key takeaways

python manage.py shell is really useful to try out the models and how the syntax works

request.user returns the user that performs the action

user.is_authenticated checks if the user is logged in or no
