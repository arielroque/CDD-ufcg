from wsgiref import headers
import scrapy
import csv
import os

class QuotesSpider(scrapy.Spider):
    name = "deputados"

    def _get_month_expenses(self, response, table_css_selector):
        expenses = {}

        table_element = response.css(table_css_selector)

        rows = table_element.css("tbody > tr")

        for row in rows:
            monthElement, expenseElement, _ = row.css("td")
            month = str(monthElement.css("::text").get()).lower()
            expense = expenseElement.css("::text").get().replace(
                ".", "").replace(",", ".")

            expenses[month] = expense

        return expenses

    def _format_dict(self, dict):
        for key in dict.keys():
            if (dict[key]):
                element = dict[key]
                element = element.strip()

                dict[key] = element

        return dict

    def start_requests(self):

        depts_file = open("lista_deputados.txt", "r")

        urls = depts_file.read().splitlines()

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={'wait': 20000})

    def parse(self, response):

        csv_dict = {}

        # ======== BASIC INFORMATION ============
        csv_dict["nome"] = response.xpath(
            '//h2[@class="nome-deputado"]/text()').get()
        csv_dict["genero"] = "M"
        csv_dict["data_nascimento"] = response.xpath(
            '//ul[@class="informacoes-deputado"]/li[5]/text()').get()

        # ======== PLENARY ATTENDANCE ============
        csv_dict["presenca_plenario"] = response.xpath(
            '//dl[@class="list-table__definition-list"]/dd[1]/text()').get()
        csv_dict["ausencia_justificada_plenario"] = response.xpath(
            '//dl[@class="list-table__definition-list"]/dd[2]/text()').get()
        csv_dict["ausencia_nao_justificada_plenario"] = response.xpath(
            '//dl[@class="list-table__definition-list"]/dd[3]/text()').get()

        # ======== COMMITTEE ATTENDANCE ============
        csv_dict["presenca_comissao"] = response.xpath(
            '//ul[@class="list-table__content"]/li[2]/dl/dd[1]/text()').get()
        csv_dict["ausencia_justificada_comissao"] = response.xpath(
            '//ul[@class="list-table__content"]/li[2]/dl/dd[2]/text()').get()
        csv_dict["ausencia_nao_justificada_comissao"] = response.xpath(
            '//ul[@class="list-table__content"]/li[2]/dl/dd[3]/text()').get()

        # ========== PARLIAMENTARY EXPENSES ==============
        csv_dict["gasto_total_par"] = response.xpath(
            '//*[@id="percentualgastocotaparlamentar"]/tbody/tr[1]/td[2]/text()').get()

        parliamentary_expenses = self._get_month_expenses(response,
                                                          "table#gastomensalcotaparlamentar")

        csv_dict["gasto_jan_par"] = parliamentary_expenses.get("jan")
        csv_dict["gasto_fev_par"] = parliamentary_expenses.get("fev")
        csv_dict["gasto_mar_par"] = parliamentary_expenses.get("mar")
        csv_dict["gasto_abr_par"] = parliamentary_expenses.get("abr")
        csv_dict["gasto_mai_par"] = parliamentary_expenses.get("mai")
        csv_dict["gasto_jun_par"] = parliamentary_expenses.get("jun")
        csv_dict["gasto_jul_par"] = parliamentary_expenses.get("jul")
        csv_dict["gasto_ago_par"] = parliamentary_expenses.get("ago")
        csv_dict["gasto_set_par"] = parliamentary_expenses.get("set")
        csv_dict["gasto_out_par"] = parliamentary_expenses.get("out")
        csv_dict["gasto_nov_par"] = parliamentary_expenses.get("nov")
        csv_dict["gasto_dez_par"] = parliamentary_expenses.get("dez")

        # =========== CABINET EXPENSE ===============
        csv_dict["gasto_total_gab"] = response.xpath(
            '//*[@id="percentualgastoverbagabinete"]/tbody/tr[1]/td[2]/text()').get()
        cabinet_expenses = self._get_month_expenses(response,
                                                    "table#gastomensalverbagabinete")
        csv_dict["gasto_jan_gab"] = cabinet_expenses.get("jan")
        csv_dict["gasto_fev_gab"] = cabinet_expenses.get("fev")
        csv_dict["gasto_mar_gab"] = cabinet_expenses.get("mar")
        csv_dict["gasto_abr_gab"] = cabinet_expenses.get("abr")
        csv_dict["gasto_mai_gab"] = cabinet_expenses.get("mai")
        csv_dict["gasto_jun_gab"] = cabinet_expenses.get("jun")
        csv_dict["gasto_jul_gab"] = cabinet_expenses.get("jul")
        csv_dict["gasto_ago_gab"] = cabinet_expenses.get("ago")
        csv_dict["gasto_set_gab"] = cabinet_expenses.get("set")
        csv_dict["gasto_out_gab"] = cabinet_expenses.get("out")
        csv_dict["gasto_nov_gab"] = cabinet_expenses.get("nov")
        csv_dict["gasto_dez_gab"] = cabinet_expenses.get("dez")

        # ============== GENERAL ===================
        csv_dict["salario"] = response.xpath(
            '//a[@class="beneficio__info"]/text()').get()[2:].strip()
        csv_dict["quant_viagem"] = response.xpath(
            '//ul[@class="recursos-beneficios-deputado-container"]/li[5]/div/a/text()').get()

        # ============== SAVE CONTENT ===================
        csv_dict = self._format_dict(csv_dict)

        file_name = "deputados.csv"
        fields = csv_dict.keys()

        if (not os.path.isfile(file_name)):
            file = open(file_name, 'w')

            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()

            file.close()

        file = open(file_name, 'a')
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writerow(csv_dict)
        file.close()
