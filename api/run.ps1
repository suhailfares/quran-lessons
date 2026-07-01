# PowerShell script
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\env\Scripts\Activate.ps1
python manage.py runserver 0.0.0.0:8000
python manage.py seed_data
python manage.py seed_quran


# Create Admin
setx ADMIN_PASSWORD "yourpassword"
# then restart terminal then
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\env\Scripts\Activate.ps1
python manage.py create_admin