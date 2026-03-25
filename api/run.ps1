# PowerShell script
& .\env\Scripts\Activate.ps1
python manage.py runserver
python manage.py seed_data
python manage.py seed_quran