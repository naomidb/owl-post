import csv
from datetime import datetime
import os
import sys
import yaml

from vivo_utils import vivo_log
from vivo_utils.connections.vivo_connect import Connection
from vivo_utils.grantication import Grantication
from vivo_utils import queries
from vivo_utils.triple_handler import TripleHandler
from vivo_utils.update_log import UpdateLog

CONFIG_PATH = '<config_file>'
_api = '--api'
_rdf = '--rdf'

def get_config(config_path):
    try:
        with open(config_path, 'r') as config_file:
            config = yaml.load(config_file.read())
    except:
        print("Error: Check config file")
        exit()
    return config

def check_filter(filter_folder, abbrev_filter, name_filter, name):
    if os.path.isdir(filter_folder):
        abbrev_path = os.path.join(filter_folder, abbrev_filter)
        name_path = os.path.join(filter_folder, name_filter)
    else:
        return name

    if os.path.isfile(abbrev_path):
        cleanfig = get_config(abbrev_path)
        abbrev_table = cleanfig.get('abbrev_table')
        name += " " #Add trailing space
        name = name.replace('\\', '')
        for abbrev in abbrev_table:
            if (abbrev) in name:
                name = name.replace(abbrev, abbrev_table[abbrev])
        name = name[:-1] #Remove final space

    if os.path.isfile(name_path):
        namefig = get_config(name_path)
        try:
            if name.upper() in namefig.keys():
                name = namefig.get(name.upper())
        except AttributeError as e:
            name = name

    return name

def process(row, grants, filter_folder):
    title = check_filter(filter_folder, 'general_filter.yaml', None, row['CLK_AWD_PROJ_NAME'].title())
    pi = row['CLK_AWD_PI']
    ps_contract_num = row['CLK_AWD_ID']
    start = row['CLK_AWD_OVERALL_START_DATE'].replace(' ', 'T')
    end = row['CLK_AWD_OVERALL_END_DATE'].replace(' ', 'T')
    awarded = round(float(row['SPONSOR_AUTHORIZED_AMOUNT']), 2)
    costs = round(float(row['DIRECT_AMOUNT']), 2)

    index_key = title + ', ' + pi + ', ' + ps_contract_num
    if index_key in grants:
        grantication = grants[index_key]
        grantication.check_dates(start, end)
        grantication.total_award += awarded
        grantication.direct_costs += costs

    else:
        grantication = Grantication()
        grantication.title = title
        grantication.pi = pi
        grantication.ps_contract_num = ps_contract_num
        grantication.sponsor_id = row['REPORTING_SPONSOR_AWD_ID']
        grantication.total_award = awarded
        grantication.direct_costs = costs
        grantication.start_date = start
        grantication.end_date = end
        grantication.award_dept = check_filter(filter_folder, 'general_filter.yaml', 'dept_filter.yaml', row['REPORTING_SPONSOR_NAME'].title())
        grantication.subcontract = check_filter(filter_folder, 'general_filter.yaml', 'dept_filter.yaml', row['CLK_AWD_SPONSOR_NAME'].title())
        grantication.admin = check_filter(filter_folder, 'general_filter.yaml', 'dept_filter.yaml', row['CLK_AWD_PI_DEPT'].title())
        grants[index_key] = grantication

    return grants

def pump_grants(connection, grantication, tripler, ulog, db_name, added_authors, added_orgs, datespans):
    matches = vivo_log.lookup(db_name, 'grants', grantication.title, 'name')
    if len(matches) >= 1:
        for match in matches:
            if (grantication.title, grantication.ps_contract_num, grantication.pi, grantication.start_date, grantication.end_date) == (match[1], match[2], match[4], match[5], match[6]):
                return
    params = queries.make_grant.get_params(connection)
    grant = params['Grant']

    start_date, start_year, start_month, start_day = parse_date(grantication.start_date)
    end_date, end_year, end_month, end_day = parse_date(grantication.end_date)
    datespan = start_date + ', ' + end_date
    if datespan in datespans:
        grant.interval_n = datespans[datespan]
    else:
        date_params = queries.make_dateTimeInterval.get_params(connection)
        date_params['start_date'].year = start_year
        date_params['start_date'].month = start_month
        date_params['start_date'].day = start_day
        date_params['end_date'].year = end_year
        date_params['end_date'].month = end_month
        date_params['end_date'].day = end_day

        tripler.update(queries.make_dateTimeInterval, **date_params)
        grant.interval_n = date_params['start_date'].interval
        datespans[datespan] = date_params['start_date'].interval

    grant.name = grantication.title
    grant.total_award_amount = grantication.total_award
    grant.direct_costs = grantication.direct_costs
    grant.sponsor_award_id = grantication.sponsor_id
    grant.ps_contract_num = grantication.ps_contract_num

    params['PI'].n_number = parse_name(connection, db_name, grantication.pi, added_authors, tripler, ulog)
    params['AwardedBy'].n_number = parse_dept(connection, db_name, grantication.award_dept, added_orgs, tripler, ulog)
    params['SubcontractedThrough'].n_number = parse_dept(connection, db_name, grantication.subcontract, added_orgs, tripler, ulog)

    tripler.update(queries.make_grant, **params)
    ulog.add_to_log('grants', grant.name, (connection.namespace + grant.n_number))

    return

def parse_date(full_datetime):
    dating, timing = full_datetime.split('T')
    year, month, day = dating.split('/')
    
    return (dating, year, month, day)

def parse_name(connection, db_name, raw_name, added_authors, tripler, ulog):
    raw_name = raw_name.title()
    try:
        last, rest = raw_name.split(',', 1)
        raw_name = last + ', ' + rest
        try:
            first, middle = rest.split(' ', 1)
        except ValueError:
            first = rest
            middle = None
    except ValueError:
        last = raw_name
        first = middle = None

    matches = vivo_log.lookup(db_name, 'authors', raw_name, 'display')
    if raw_name in added_authors.keys():
        matches.append(added_authors[raw_name])

    if len(matches) == 0:
        matches = vivo_log.lookup(db_name, 'authors', raw_name, 'display', True)
    if len(matches) == 1:
        author_n = matches[0][0]
    else:
        params = queries.make_person.get_params(connection)
        params['Author'].name = raw_name
        params['Author'].last = last
        if first:
            params['Author'].first = first
        if middle:
            params['Author'].middle = middle
        params['Author'].ufentity = True
        params['Author'].ufcurrententity = True
        tripler.update(queries.make_person, **params)

        author_n = params['Author'].n_number
        ulog.add_to_log('authors', raw_name, (connection.namespace + author_n))
        added_authors[raw_name] = author_n 
        if len(matches) > 1:
            auth_n_list = [author_n]
            for match in matches:
                auth_n_list.append(match[0])
            ulog.track_ambiguities(raw_name, auth_n_list)
    return author_n

def parse_dept(connection, db_name, org_name, added_orgs, tripler, ulog, org_type='organization'):
    matches = vivo_log.lookup(db_name, 'organizations', org_name, 'name')
    if org_name in added_orgs.keys():
        matches.append(added_orgs[org_name])

    if len(matches) == 0:
        matches = vivo_log.lookup(db_name, 'organizations', org_name, 'name', True)
    if len(matches) == 1:
        org_n = matches[0][0]
    else:
        params = queries.make_organization.get_params(connection)
        params['Organization'].name = org_name
        params['Organization'].type = org_type
        tripler.update(queries.make_organization, **params)

        org_n = params['Organization'].n_number
        ulog.add_to_log('organizations', org_name, (connection.namespace + org_n))
        added_orgs[org_name] = org_n
        if len(matches) > 1:
            org_n_list = [org_n]
            for match in matches:
                org_n_list.append(match[0])
            ulog.track_ambiguities(org_name, org_n_list)
    return org_n

def main(args):
    config = get_config(args[CONFIG_PATH])
    namespace = config.get('namespace')
    email = config.get('email')
    password = config.get('password')
    update_endpoint = config.get('update_endpoint')
    query_endpoint = config.get('query_endpoint')
    filter_folder = config.get('filter_folder')

    db_name = '/tmp/vivo_temp_storage.db'

    try:
        connection = Connection(namespace, email, password, update_endpoint, query_endpoint)
        vivo_log.update_db(connection, db_name, ['authors', 'organizations', 'grants'])
    
        now = datetime.now()
        timestamp = now.strftime("%Y_%m_%d")
        full_path = os.path.join(config.get('folder_for_logs'),
            now.strftime("%Y")+ '/' + now.strftime("%m") + '/' + now.strftime("%d"))
        try:
            os.makedirs(full_path)
        except FileExistsError:
            pass

        disam_file = os.path.join(full_path, (timestamp + '_grant_disambiguation.json'))
        output_file = os.path.join(full_path, (timestamp + '_grant_output_file.txt'))
        upload_file = os.path.join(full_path, (timestamp + '_grant_upload_log.txt'))
        skips_file = os.path.join(full_path, (timestamp + '_grant_skips.json'))
        
        meta = {'source': 'Errol', 'harvest_date': now.strftime("%Y-%m-%d")}
        tripler = TripleHandler(args[_api], connection, meta, output_file)
        ulog= UpdateLog()

        grant_fields = ['awards_history_id', 'CLK_AWD_ID', 'CLK_AWD_STATE', 'CLK_AWD_PI', 'CLK_PI_UFID',
                        'REPORTING_SPONSOR_NAME', 'REPORTING_SPONSOR_CUSTID', 'REPORTING_SPONSOR_CAT',
                        'REPORTING_SPONSOR_AWD_ID', 'DIRECT_AMOUNT', 'INDIRECT_AMOUNT', 'SPONSOR_AUTHORIZED_AMOUNT',
                        'FUNDS_ACTIVATED', 'CLK_AWD_PI_DEPTID', 'CLK_AWD_PI_DEPT', 'CLK_AWD_PI_COLLEGE',
                        'CLK_AWD_DEPT', 'CLK_AWD_COLLEGE', 'CLK_AWD_DEPTID', 'CLK_AWD_SPONSOR_NAME',
                        'CLK_AWD_SPONSOR_CUSTID', 'CLK_AWD_SPONSOR_CAT', 'CLK_AWD_SPONSOR_AWD_ID',
                        'CLK_AWD_PRIME_SPONSOR_NAME', 'CLK_AWD_PRIME_SPONSOR_CUSTID', 'CLK_AWD_PRIME_SPONSOR_CAT',
                        'CLK_AWD_PRIME_SPONSOR_AWD_ID', 'CLK_AWD_OVERALL_START_DATE', 'CLK_AWD_OVERALL_END_DATE',
                        'CLK_AWD_COST_SHARE', 'CLK_AWD_HUMAN_SUBJ', 'CLK_AWD_LAB_ANMLS', 'CLK_AWD_PROJ_ID',
                        'CLK_AWD_PROJ_NAME', 'CLK_AWD_PROJ_MGR', 'CLK_AWD_PROJ_MGR_UFID', 'CLK_AWD_PROJ_DEPT',
                        'CLK_AWD_PROJ_DEPTID', 'CLK_AWD_PROJ_COLLEGE', 'CLK_AWD_PROJ_COLLEGEID',
                        'CLK_AWD_ALLOC_IDC_RATE', 'CLK_AWD_ALLOC_RATE_TYPE', 'CLK_AWD_ALLOC_RATE_BASE',
                        'CLK_AWD_PURPOSE', 'CLK_AWD_PROJ_TYPE', 'CLK_AWD_PRJ_START_DT', 'CLK_AWD_PRJ_END_DT',
                        'CLK_AWD_ALLOC_STRT_DT', 'CLK_AWD_ALLOC_END_DT', 'CLK_AWD_PS_FUND_CODE_ID',
                        'CLK_AWD_PROJ_ACTIVE', 'CLK_AWD_PROJ_CLOSED', 'SRC', 'MOD_PAY_ID', 'ALLOCATION_ID',
                        'SID_DATE_ACTVTD', 'DAY_NUM_DATE_ACTIVATED', 'LEAP_YEAR', 'FD_DATE_ACTIVATED',
                        'MONTH_DATE_ACTIVATED', 'FM_DATE_ACTIVATED', 'FQ_DATE_ACTIVATED', 'FY_DATE_ACTIVATED',
                        'CLK_AWD_FULL_TITLE', 'EXCEPTION', 'INTERNAL_REPORTING_SPONSOR', 'TRANSFER', 'AWD_PI_PREEM',
                        'PRJ_MGR_PREEM', 'UNIVERSITY_REPORTABLE', 'TEMPORARY_IND', 'CARRYOVER',
                        'CORE_OFFICE_CORRECTION', 'INTERNAL_FUNDS', 'LASTUPD_EW_DTTM', 'CLK_AWD_PROJ_MGR_DEPTID',
                        'CLK_AWD_PROJ_MGR_DEPT', 'CLK_AWD_PROJ_MGR_COLLEGEID', 'CLK_AWD_PROJ_MGR_COLLEGE',
                        'CLK_MOD_SPON_AWD_ID', 'AcademicUnit', 'Roster2008', 'Roster2009', 'Roster2010', 'Roster2011',
                        'Roster2012', 'Roster2013', 'Roster2014', 'Roster2015', 'Roster2016', 'Roster2017', 'Roster2018']

        with open(config.get('grant_file'), 'r') as grantfile:
            reader = csv.DictReader(grantfile, fieldnames=grant_fields)
            next(reader)
            grants = {}
            for row in reader:
                grants = process(row, grants, filter_folder)
            
        added_authors = {}
        added_orgs = {}
        datespans = {}    
        for grant in grants.values():
            pump_grants(connection, grant, tripler, ulog, db_name, added_authors, added_orgs, datespans)

        file_made = ulog.create_file(upload_file)
        ulog.write_skips(skips_file)
        ulog.write_disam_file(disam_file)

        if args[_rdf]:
            rdf_file = timestamp + '_upload.rdf'
            rdf_filepath = os.path.join(full_path, rdf_file)
            tripler.print_rdf(rdf_filepath)

    except Exception as e:
        print("Error")
        os.remove(db_name)
        import traceback
        exit(traceback.format_exc())