import os
import logging
from supabase import create_client, Client

# Configuração de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class GerenciamentoReservasSupabase:
    def __init__(self, supabase_url=None, supabase_key=None):
        """
        Inicializa o cliente Supabase.
        """
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_KEY")
        self.supabase: Client = None

        if not self.supabase_url or not self.supabase_key:
            logging.error("Supabase URL ou chave não foram fornecidos. Cliente Supabase não será inicializado.")
            return

        try:
            self.supabase = create_client(self.supabase_url, self.supabase_key)
            logging.info("Cliente Supabase configurado com sucesso.")
        except Exception as e:
            logging.error(f"Erro ao inicializar o cliente Supabase: {e}")

    def fetch_table(self, table_name, limit=None, order_by=None):
        """
        Busca dados de uma tabela.

        Args:
            table_name (str): Nome da tabela.
            limit (int, opcional): Número máximo de registros.
            order_by (str, opcional): Campo de ordenação.

        Returns:
            list: Registros da tabela ou lista vazia em caso de erro.
        """
        if not self.supabase:
            logging.error("Cliente Supabase não inicializado.")
            return []

        try:
            query = self.supabase.table(table_name).select("*")
            if order_by:
                query = query.order(order_by)
            if limit:
                query = query.limit(limit)
            response = query.execute()
            return response.data
        except Exception as e:
            logging.error(f"Erro ao buscar dados da tabela {table_name}: {e}")
            return []

    

    def buscar_reservas_com_imoveis(self, order_by=None):
     """
     Busca reservas com informações dos imóveis relacionadas.

     Args:
        order_by (str, opcional): Campo para ordenar os resultados.

     Returns:
        list: Lista de reservas com dados dos imóveis ou lista vazia em caso de erro.
    """
     if not self.supabase:
        logging.error("Cliente Supabase não inicializado.")
        return []

     try:
        # Modifique os nomes das tabelas e colunas conforme a estrutura do seu banco de dados.
        query = self.supabase.rpc(
            "buscar_reservas_com_imoveis",  # Função remota no banco de dados
            {}  # Parâmetros adicionais, se necessário
        )
        if order_by:
            query = query.order(order_by)
        response = query.execute()
        return response.data
     except Exception as e:
        logging.error(f"Erro ao buscar reservas com imóveis: {e}")
        return []






    def insert_row(self, table_name, data):
        """
        Insere uma nova linha na tabela.

        Args:
            table_name (str): Nome da tabela.
            data (dict): Dados para inserção.

        Returns:
            bool: True se a inserção for bem-sucedida, False caso contrário.
        """
        if not self.supabase or not isinstance(data, dict):
            logging.error("Dados inválidos ou cliente Supabase não inicializado.")
            return False

        try:
            response = self.supabase.table(table_name).insert(data).execute()
            if response.status_code != 201:
                logging.error(f"Erro ao inserir dados na tabela {table_name}: {response.status_code}")
                return False
            logging.info(f"Dados inseridos com sucesso na tabela {table_name}.")
            return True
        except Exception as e:
            logging.error(f"Erro ao inserir dados: {e}")
            return False

    def update_row(self, table_name, row_id, data):
        """
        Atualiza uma linha da tabela.

        Args:
            table_name (str): Nome da tabela.
            row_id (int): ID da linha a ser atualizada.
            data (dict): Dados para atualização.

        Returns:
            bool: True se a atualização for bem-sucedida, False caso contrário.
        """
        if not self.supabase or not isinstance(data, dict):
            logging.error("Dados inválidos ou cliente Supabase não inicializado.")
            return False

        try:
            response = self.supabase.table(table_name).update(data).eq("id", row_id).execute()
            if response.status_code != 200:
                logging.error(f"Erro ao atualizar a linha {row_id} na tabela {table_name}: {response.status_code}")
                return False
            logging.info(f"Linha {row_id} atualizada com sucesso na tabela {table_name}.")
            return True
        except Exception as e:
            logging.error(f"Erro ao atualizar dados: {e}")
            return False

    def adicionar_reserva(self, nome_hospede, entrada, saida, imovel_id, nome_parceiro):
     """
     Adiciona uma nova reserva.
    
     Args:
        nome_hospede (str): Nome do hóspede.
        entrada (str): Data de entrada no formato YYYY-MM-DD.
        saida (str): Data de saída no formato YYYY-MM-DD.
        imovel_id (int): ID do imóvel vinculado à reserva.
        nome_parceiro (str): Nome do parceiro.

     Returns:
        bool: True se a reserva for adicionada com sucesso, False caso contrário.
     """
     if entrada >= saida:
        logging.error("A data de entrada deve ser anterior à data de saída.")
        return False

     # Verificar se o imóvel com o ID fornecido existe
     imovel = self.supabase.table("imoveisbeta").select("id").eq("id", imovel_id).execute()
     if not imovel.data:
        logging.error(f"O imóvel com ID {imovel_id} não existe na tabela 'imoveisbeta'.")
        return False

     # Inserir a nova reserva na tabela 'betareservas'
     data = {
        "nome_hospede": nome_hospede,
        "entrada": entrada,
        "saida": saida,
        "imovel_id": imovel_id,
        "nome_parceiro": nome_parceiro,
    }
     return self.insert_row("betareservas", data)

    



    def editar_reserva(self, id_reserva, **kwargs):
       """
        Edita uma reserva existente.

       Args:
        id_reserva (int): ID da reserva.
        **kwargs: Campos para atualização.

       Returns:
        bool: True se bem-sucedido, False caso contrário.
        """
        # Validar que a data de entrada é anterior à data de saída, se fornecidas
       entrada = kwargs.get("entrada")
       saida = kwargs.get("saida")
       if entrada and saida and entrada >= saida:
          logging.error("A data de entrada deve ser anterior à data de saída.")
          return False

    # Validar se o imóvel fornecido existe, caso o ID do imóvel seja fornecido
       imovel_id = kwargs.get("imovel_id")
       if imovel_id:
        imovel = self.supabase.table("imoveisbeta").select("id").eq("id", imovel_id).execute()
        if not imovel.data:
            logging.error(f"O imóvel com ID {imovel_id} não existe na tabela 'imoveisbeta'.")
            return False

    # Garantir que pelo menos um campo seja atualizado
        if not kwargs:
            logging.error("Nenhum campo para atualizar foi fornecido.")
            return False

    # Atualizar a reserva na tabela
       try: 
         response = self.supabase.table("betareservas").update(kwargs).eq("id", id_reserva).execute()
         if response.status_code == 200:  # Status de sucesso para atualizações
            logging.info(f"Reserva com ID {id_reserva} atualizada com sucesso.")
            return True
         else:
            logging.error(f"Erro ao atualizar a reserva com ID {id_reserva}: {response.status_code}")
            return False
       except Exception as e:
        logging.error(f"Erro inesperado ao atualizar a reserva: {e}")
        return False

    def adicionar_imovel(self, numero_apto, bloco, condominio, proprietario):
        """
        Adiciona um novo imóvel.

        Args:
            numero_apto (str): Número do apartamento.
            bloco (str): Bloco do imóvel.
            condominio (str): Nome do condomínio.
            proprietario (str): Nome do proprietário.

        Returns:
            bool: True se bem-sucedido, False caso contrário.
        """
        data = {
            "numero_apto": numero_apto,
            "bloco": bloco,
            "condominio": condominio,
            "proprietario": proprietario,
        }
        return self.insert_row("imoveisbeta", data)

    def editar_imovel(self, id_imovel, **kwargs):
        """
        Edita um imóvel existente.

        Args:
            id_imovel (int): ID do imóvel.
            **kwargs: Campos para atualização.

        Returns:
            bool: True se bem-sucedido, False caso contrário.
        """
        return self.update_row("imoveisbeta", id_imovel, kwargs)
