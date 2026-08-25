import os
from datetime import datetime

import gspread


class SheetsHandler:
    def __init__(self, spreadsheet_id=None, credentials_file=None):
        self.spreadsheet_id = (spreadsheet_id or os.environ.get("SPREADSHEET_ID", "")).strip()
        self.credentials_file = (
            credentials_file
            or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "service_account.json")
        )
        self.gc = None
        self.worksheet = None
        self.connect()

    def connect(self):
        if not self.spreadsheet_id:
            print("SPREADSHEET_ID não definido. Configure no arquivo .env")
            self.worksheet = None
            return

        if not os.path.isfile(self.credentials_file):
            print(
                f"Arquivo de credenciais não encontrado: {self.credentials_file}. "
                "Copie service_account.example.json para service_account.json "
                "e substitua pelo JSON real do Google Cloud."
            )
            self.worksheet = None
            return

        try:
            self.gc = gspread.service_account(filename=self.credentials_file)
            spreadsheet = self.gc.open_by_key(self.spreadsheet_id)
            self.worksheet = spreadsheet.sheet1
            print("Conectado ao Google Sheets via ID com sucesso!")
        except Exception as e:
            print(f"Erro ao conectar ao Google Sheets: {e}")
            self.worksheet = None

    def registrar_ponto(self, nome, tipo):
        if not self.worksheet:
            self.connect()
            if not self.worksheet:
                return False, "Erro de conexão com a planilha."

        agora = datetime.now()
        data = agora.strftime("%d/%m/%Y")
        hora = agora.strftime("%H:%M:%S")

        try:
            self.worksheet.append_row([nome, data, hora, tipo])
            return True, f"Ponto de {tipo} registrado com sucesso para {nome} às {hora}!"
        except Exception as e:
            return False, f"Erro ao salvar no Google Sheets: {e}"
