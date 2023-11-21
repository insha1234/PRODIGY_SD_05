[10:29 pm, 21/11/2023] Muskan : import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


def single_ngo_scrapper(driver: webdriver.Chrome, state_name: str, ngo_name: str, ngo_link: str) -> None:
    cur_ngo_data: dict[str, str] = {
        'State': state_name,
        'NGO name': ngo_name,
        'NGO link': ngo_link,
        'Address': '',
        'PIN Code': '',
        'Phone': '',
        'Mobile': '',
        'Email': '',
        'Website': '',
        'Contact Person': '',
        'Purpose': '',
        'Aims/Objectives/Mission': '',
    }
    driver.get(ngo_link)

    all_cur_data = driver.find_element(
        By.CSS_SELECTOR, 'div.npos-postcontent:nth-child(3) > p:nth-child(1)').text

    # Scrapping only animal related NGOs
    # if 'animal' not in all_cur_data.lower():
    #     return

    all_cur_data = all_cur_data.split('\n')
    for i in all_cur_data:
        if 'add.:' in i.lower() or 'add. :' in i.lower() or 'add :' in i.lower() or 'add:' in i.lower():
            cur_ngo_data['Address'] = i.split(':')[-1].strip()
        elif 'pin:' in i.lower() or 'pin :' in i.lower():
            cur_ngo_data['PIN Code'] = i.split(':')[-1].strip()
        elif 'phone:' in i.lower() or 'phone :' in i.lower():
            cur_ngo_data['Phone'] = i.split(':')[-1].strip()
        elif 'mobile:' in i.lower() or 'mobile :' in i.lower():
            cur_ngo_data['Mobile'] = i.split(':')[-1].strip()
        elif 'email:' in i.lower() or 'email :' in i.lower():
            cur_ngo_data['Email'] = i.split(':')[-1].strip()
        elif 'website:' in i.lower() or 'website :' in i.lower():
            cur_ngo_data['Website'] = i.split(':')[-1].strip()
        elif 'contact person:' in i.lower() or 'contact person :' in i.lower():
            cur_ngo_data['Contact Person'] = i.split(':')[-1].strip()
        elif 'purpose:' in i.lower() or 'purpose :' in i.lower():
            cur_ngo_data['Purpose'] = i.split(':')[-1].strip()
        elif 'aims/Objectives/mission:' in i.lower() or 'aims/objectives/mission :' in i.lower():
            cur_ngo_data['Aims/Objectives/Mission'] = i.split(':')[-1].strip()

    # Checking if csv file exists already or not.
    try:
        with open('output.csv', 'r') as _:
            exists = 1
    except:
        exists = 0
    # Feeding data into output csv
    with open('output.csv', 'a') as output_csv:
        csv_writer = csv.DictWriter(
            output_csv, fieldnames=list(cur_ngo_data.keys()))
        if exists == 0:
            csv_writer.writeheader()
        csv_writer.writerow(cur_ngo_data)


def single_state_scrapper(driver: webdriver.Chrome, state_name: str, state_link: str) -> None:
    # Collecting all NGO links of current state
    all_ngo_links: dict[str, str] = {}
    li: int = 1
    page: int = 1
    try:
        while True:
            driver.get(str(state_link + f'?lcp_page0={page}#lcp_instance_0'))
            page += 1
            # Checking if current page has data or not
            # If it has no data then this will throw an exception and exit the loop
            _ = driver.find_element(
                By.CSS_SELECTOR, '#lcp_instance_0 > li:nth-child(1)')
            # Scrapping current page
            try:
                while True:
                    try:
                        cur_link: str = driver.find_element(
                            By.CSS_SELECTOR, f'#lcp_instance_0 > li:nth-child({li}) > a:nth-child(1)').get_attribute('href')
                    except:
                        cur_link: str = driver.find_element(
                            By.CSS_SELECTOR, f'#lcp_instance_0 > li:nth-child({li}) > strong:nth-child(1) > a:nth-child(1)').get_attribute('href')
                    cur_ngo_name: str = driver.find_element(
                        By.CSS_SELECTOR, f'#lcp_instance_0 > li:nth-child({li})').text
                    all_ngo_links[cur_ngo_name] = cur_link
                    li += 1
            except:
                pass
    except:
        pass

    # Scrapping each NGO one by one
    for i in all_ngo_links:
        single_ngo_scrapper(
            driver, state_name, i, all_ngo_links[i])


def main() -> None:
    # Starting up selenium web driver.
    chrome_browser_options = Options()
    chrome_browser_options.add_experimental_option(
        'useAutomationExtension', False)
    chrome_browser_options.add_experimental_option(
        'excludeSwitches', ['enable-automation'])
    chrome_browser_options.add_argument(
        '--ignore-ssl-errors=yes')
    chrome_browser_options.add_argument(
        '--ignore-certificate-errors')
    driver = webdriver.Chrome(options=chrome_browser_options)

    # Scrapping state links
    state_links: dict[str, str] = {}
    driver.get('https://ngosindia.org/')
    li: int = 1
    try:
        while True:
            try:
                cur_link: str = driver.find_element(
                    By.XPATH, f'/html/body/div[1]/div/div[1]/div/div/div[2]/article/div/div[2]/div/div/div[2]/ul/li[{li}]/a').get_attribute('href')
            except:
                cur_link: str = driver.find_element(
                    By.XPATH, f'/html/body/div[1]/div/div[1]/div/div/div[2]/article/div/div[2]/div/div/div[2]/ul/li[{li}]/strong/a').get_attribute('href')
            cur_state_name: str = driver.find_element(
                By.XPATH, f'/html/body/div[1]/div/div[1]/div/div/div[2]/article/div/div[2]/div/div/div[2]/ul/li[{li}]').text
            state_links[cur_state_name] = cur_link
            li += 1
    except:
        pass

    # Asking the name of state to scrape
    count: int = 1
    state_names: list[str] = list(state_links.keys())
    print('Available States:')
    print('    0 == ALL States')
    for i in state_names:
        print(f'    {count} == {i}')
        count += 1
    to_scrape = int(
        input('Enter the number of state you want to scrape: '))
    print('Worling on it...')
    if to_scrape == 0:
        # Scrapping each state one by one
        for i in state_links:
            single_state_scrapper(driver, i, state_links[i])
    else:
        to_scrape -= 1
        single_state_scrapper(
            driver, state_names[to_scrape], state_links[state_names[to_scrape]])


if _name_ == '_main_':
    main()
[10:29 pm, 21/11/2023] Muskan : # local env
.vscode
output.csv

# Byte-compiled / optimized / DLL files
_pycache_/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Translations
*.mo
*.pot
  # Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
.pybuilder/
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
#   For a library or package, you might want to ignore these files since the code is
#   intended to run in multiple environments; otherwise, check them in:
# .python-version

# pipenv
#   According to pypa/pipenv#598, it is recommended to include Pipfile.lock in version control.
#   However, in case of collaboration, if having platform-specific dependencies or dependencies
#   having no cross-platform support, pipenv may install dependencies that don't work, or not
#   install all needed dependencies.
#Pipfile.lock

# poetry
#   Similar to Pipfile.lock, it is generally recommended to include poetry.lock in version control.
#   This is especially recommended for binary packages to ensure reproducibility, and is more
#   commonly ignored for libraries.
#   https://python-poetry.org/docs/basic-usage/#commit-your-poetrylock-file-to-version-control
#poetry.lock

# pdm
#   Similar to Pipfile.lock, it is generally recommended to include pdm.lock in version control.
#pdm.lock
#   pdm stores project-wide configurations in .pdm.toml, but it is recommended to not include it
#   in version control.
#   https://pdm.fming.dev/#use-with-ide
.pdm.toml

# PEP 582; used by e.g. github.com/David-OConnor/pyflow and github.com/pdm-project/pdm
_pypackages_/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/

# PyCharm
#  JetBrains specific template is maintained in a separate JetBrains.gitignore that can
#  be found at https://github.com/github/gitignore/blob/main/Global/JetBrains.gitignore
#  and can be added to the global gitignore or merged into this file.  For a more nuclear
#  option (not recommended) you can uncomment the following to ignore the entire idea folder.
#.idea/
