import logging

logging.basicConfig(filename='log_file.log', filemode='a',
                    format='%(filename)s [LINE:%(lineno)d] #%(levelname)s [%('
                           'asctime)s]  %(message)s',
                    level=logging.INFO)
logging.warning('Это будет записано в log-файл')
