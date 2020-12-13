import os
import re
import shutil
from os import path, replace, remove
from pathlib import Path
from ftplib import FTP, all_errors

import config
from config import get_config
from load import save_load, read_load, delete_load
from strava import strava_do_update
from velohero import velohero_check_sso_login
from velohero import velohero_do_update
from velohero import velohero_do_upload
import utility


def _prepare_archive(destination, load):
    """
    Checks if destination exists and returns a user human path. If destination directory is missing, it will be
    created. Exit in error case.

    :param: destination String with destination information, from Config or command line
    :param: load Load with file name

    :returns: dict with
        ftp [true\false]
        overwrite [true\false]
        dest_dir path without file name
        host FTP Host address or None
        username FTP Username or None
        password FTP Password or None
    """
    ret = dict()

    ret['ftp'] = destination.strip().lower().startswith("use ftp")
    ret['overwrite'] = None
    ret['dest_dir'] = None
    ret['host'] = None
    ret['username'] = None
    ret['password'] = None

    if ret['ftp']:
        regex = re.match(".* username=(.*?)( .*|$)", destination)
        if regex and regex.group(1):
            ret['username']=regex.group(1)
        else:
            utility.exit_on_error(f"Missing username in destination configuration '{destination}'")

        regex = re.match(".* password=(.*?)( .*|$)", destination)
        if regex and regex.group(1):
            ret['password']=regex.group(1)
        else:
            utility.exit_on_error(f"Missing password in destination configuration '{destination}'")

        regex = re.match(".* host=(.*?)( .*|$)", destination)
        if regex and regex.group(1):
            ret['host']=regex.group(1)
        else:
            utility.exit_on_error(f"Missing host in destination configuration '{destination}'")

        regex = re.match(".* dir=(.*?)( .*|$)", destination)
        if regex and regex.group(1):
            ret['dest_dir'] = utility.resolve_path(regex.group(1), load.started_at)
        else:
            utility.exit_on_error(f"Missing dir in destination configuration '{destination}'")

        with FTP(host=ret['host'], user=ret['username'], passwd=ret['password']) as connection:
            utility.log("FTP", connection.getwelcome())

            # Check if directory exists
            try:
                connection.cwd(ret['dest_dir'])
                exists = True
            except all_errors:
                exists = False

            # Let's try to create it
            if not exists:
                try:
                    connection.mkd(ret['dest_dir'])
                    connection.cwd(ret['dest_dir'])
                except all_errors:
                    utility.exit_on_error(f"Could not create directory via FTP: '{ret['dest_dir']}'")
                    return

            # Now we have an existing destination dir
            try:
                pathlist = connection.nlst()
                ret['overwrite']  = Path(load.file_name).name in pathlist
            except all_errors as e:
                utility.exit_on_error(e)
                return ret

    else:
        ret['dest_dir'] = utility.resolve_path(destination, load.started_at)

        if not path.exists(ret['dest_dir']):
            print(f"Directory not there, create it: {ret['dest_dir']}")
            Path(ret['dest_dir']).mkdir(parents=True, exist_ok=True)

        if not path.exists(ret['dest_dir']):
            utility.exit_on_error(f"Destination doesn't exist:'{ret['dest_dir']}'")

        ret['overwrite'] = path.exists(path.join(ret['dest_dir'], load.file_name))


    return ret


def _execute_archive(preparation, load):

    dest = path.join(preparation['dest_dir'], Path(load.file_name).name)
    if preparation['ftp']:
        try:
            with FTP(host=preparation['host'], user=preparation['username'], passwd=preparation['password']) as connection:
                with open(load.file_name, 'rb') as f:
                    connection.storlines(f"STOR {dest}", f)
                    human_dest = f"{preparation['host']}/{dest}"

        except all_errors as e:
            utility.exit_on_error(f"Archiving failed: {e}")

        os.remove(load.file_name)

    else:
        utility.log("os.replace from {} to".format(load.file_name), preparation['dest_dir'])
        dest = path.join(preparation['dest_dir'], Path(load.file_name).name)
        shutil.move(load.file_name, dest)
        human_dest=dest

    load.set_archived_to(dest)
    delete_load()
    print("Archived to: '{}'".format(human_dest))




def process_transfer(args):
    # utility.log("process_transfer", "start")

    if not args.velohero and not args.archive and not args.strava and not args.dir and not args.purge:
        utility.exit_on_error("Missing transfer destination(s). Use --help to see possible arguments")

    load = read_load()

    if load is None:
        utility.exit_on_error("No file loaded! Use 'load' to stage the next activity.")

    if args.purge:
        if args.purge != path.basename(load.file_name):
            utility.exit_on_error(f"Wrong filename. You can only purge the loaded file {path.basename(load.file_name)}")
        else:
            remove(load.file_name)
            delete_load()
            print("File and Load purged")
            return

    if args.strava and load.strava_activity_id is None:
        utility.exit_on_error("STRAVA activity not loaded, so STRAVA can't be updated. If you want to update your STRAVA activity, " 
                      "first 'load --strava' to get the activity ID from STRAVA.")

    if not path.exists(load.file_name):
        utility.exit_on_error("File not found: '{}'".format(load.file_name))
        
    if load.new_activity_type is None:
        utility.exit_on_error(f"Activity type not set! Use heroscript set --activity_type '{utility.activity_type_list}'")
        
    archive_preparation = None

    if args.dir or args.archive:
        if args.dir:
            archive_preparation = _prepare_archive(args.dir, load)

        if args.archive:
            archive_preparation = _prepare_archive(get_config(config.key_archive_dir), load)

        if archive_preparation['overwrite']:
            print(f"[WARN] Archive file already exists, will be overwritten.")

    if args.velohero:

        # Velohero step 2: Upload, if not already done
        if load.velohero_workout_id is None:
            print("Upload to velohero.", end='', flush=True)

            velohero_check_sso_login()
            print(".", end='', flush=True)

            velohero_workout_id = velohero_do_upload(load.file_name)

            load.set_velohero_workout_id(velohero_workout_id)
            print(".", end='', flush=True)

            save_load(load)

            velohero_do_update(velohero_workout_id, None, load)

            print("Done (new Workout ID %s created)" % velohero_workout_id)

        # Velohero step update
        else:
            print("Update velohero.", end='', flush=True)

            velohero_check_sso_login()
            print(".", end='', flush=True)

            velohero_workout_id = load.velohero_workout_id

            # Velohero step update
            velohero_do_update(velohero_workout_id, None, load)

            print("Done (Workout ID %s updated)" % velohero_workout_id)

    if args.strava:
        strava_do_update()

    if args.dir or args.archive:

        _execute_archive(archive_preparation, load)

