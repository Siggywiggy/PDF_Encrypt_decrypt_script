#! python3
# a script that will scan trough every PDF in a folder and its subfolders
# encrypts or decrypts PDF-s with password provided and adds a suffix to filename

import PyPDF2
import os
import logging
import re
from pathlib import Path
from send2trash import send2trash

# comment out to enable logging
# logging.disable(logging.CRITICAL)

logging.basicConfig(
    level=logging.DEBUG, format=" %(asctime)s -  %(levelname) s -  %(message)s"
)

logging.debug("Start of program")

# choose decrypt or encrypt files
action = 'encrypt'
#choose password to use for encryption/decryption
passphrase = 'swordfish'
# set the starting folder
starting_folder = Path.cwd() / 'PDF_tree'
logging.debug(f'the starting location is {starting_folder}')
# regex filename pattern

pdf_filename_pattern = re.compile(r'(.*?)(?:_encrypted|_decrypted)?(\.pdf)')
# capture group non-greedy all before optional encrypted|decrypted non-capture group
# followed by .pdf file extension

# encrypt function
def encrypt_pdf(filename, passphrase):
    pdf_reader = PyPDF2.PdfFileReader(open(filename, 'rb'))
    if not pdf_reader.isEncrypted: # if the file is encrypted
        pdf_writer = PyPDF2.PdfFileWriter()
        # copying the files content over to new pdf_writer object
        for page_num in range(pdf_reader.numPages):
            pdf_writer.addPage(pdf_reader.getPage(page_num))
        pdf_writer.encrypt(passphrase)
        return pdf_writer
    else:
        print(f'{filename} is already encrypted')
        return None

# decrypt function
def decrypt_pdf(filename, passphrase):
    pdf_reader = PyPDF2.PdfFileReader(open(filename, 'rb'))
    if pdf_reader.isEncrypted:
        try:
            pdf_reader.decrypt(passphrase) # decrypt the original file
            pdf_writer = PyPDF2.PdfFileWriter() # open a pdf file writer object
            for page_num in range(pdf_reader.numPages):
                pdf_writer.addPage(pdf_reader.getPage(page_num)) # add all the pages
            return pdf_writer
        except PyPDF2.utils.PdfReadError as err:
            print(f'something went wrong with opening the file {os.path.basename(filename)}: {err}')
            return None
    else:
        print(f'{filename} is not encrypted')
        return None


# walk the folder with os.walk()
for folder_name, sub_folders, file_names in os.walk(starting_folder):
    logging.debug(f'file names are {file_names}')
    logging.debug(f'folder name is {folder_name}')
    for file_name in file_names:
        match_object = pdf_filename_pattern.search(file_name)
        if match_object: # if a regex hit
            logging.debug(f'regex match object groups are {match_object.groups()}')
            if action == 'encrypt':
                # open the file and encrypt it
                full_file_name = Path(folder_name) / file_name
                logging.debug(f'the full file name is {full_file_name}')
                pdf_writer = encrypt_pdf(full_file_name, passphrase)
                if pdf_writer is not None:
                    # save the file with suffix _encrypted.pdf
                    new_file_name = Path(folder_name) / (match_object.group(1) + '_encrypted' + match_object.group(2))
                    result_pdf = open(new_file_name, 'wb')
                    pdf_writer.write(result_pdf)
                    result_pdf.close()
                # Attempt to decrypt the file, if successful delete original file
                if decrypt_pdf(new_file_name, passphrase) is not None:
                    print(f'deleting {file_name}')
                    # send2trash(full_file_name)
                    send2trash(full_file_name)
                else:
                    print(f'failed to decrypt {file_name}!')
            elif action == 'decrypt':
                full_file_name = Path(folder_name) / file_name
                logging.debug(f'the full file name is {full_file_name}')
                pdf_writer = decrypt_pdf(full_file_name, passphrase)
                if pdf_writer is not None: # if the file is encrypted
                    new_file_name = Path(folder_name) / (match_object.group(1) + '_decrypted' + match_object.group(2))
                    result_pdf = open(new_file_name, 'wb')
                    pdf_writer.write(result_pdf)
                    result_pdf.close()
                    send2trash(full_file_name) # delete the original encrypted file
                else:
                    print(f'{file_name} is not encrypted')
                    continue

        else: #if no regex hit
            continue
