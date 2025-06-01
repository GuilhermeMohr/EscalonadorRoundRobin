class DataRow:
    def __init__(self, id, tempoChegada, execucao, hasBloqueio, espera, execucao2):
        self.id = id
        self.tempoChegada = tempoChegada
        self.execucao = execucao
        self.hasBloqueio = hasBloqueio
        self.espera = espera
        self.execucao2 = execucao2
    
    def __repr__(self):
        return (f"DataRow(col1={self.id}, col2={self.tempoChegada}, "
                f"col3={self.execucao}, col4={self.hasBloqueio}, "
                f"col5={self.espera}, col6={self.execucao2})")

def read_file_to_objects(filename):
    def parse_line(line):
        parts = [part.strip() for part in line.split('|')]
        col1 = int(parts[0])
        col2 = int(parts[1])
        col3 = parts[2].strip('"')
        col4 = parts[3].lower() == 'true'
        col5 = int(parts[4])
        col6 = parts[5].strip('"')
        return DataRow(col1, col2, col3, col4, col5, col6)
    
    processes = []
    with open(filename, 'r') as file:
        for line in file:
            if line.strip():
                data_row = parse_line(line)
                processes.append(data_row)
    return processes

# if __name__ == "__main__":
#     filename = 'processes.txt' 
#     rows = read_file_to_objects(filename)
#     for row in rows:
#         print(row)