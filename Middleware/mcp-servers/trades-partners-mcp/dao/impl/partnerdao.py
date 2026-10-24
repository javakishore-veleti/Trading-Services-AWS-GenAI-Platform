from common.dtos.req_resp_dtos import GetPartnerRequest, ListPartnersRequest, PartnerDto, PartnerRowDto, PartnerRowsDto
from dao.interfaces import PartnerDao


class PartnerDaoImpl(PartnerDao):
    _partners: list[PartnerDto] = [
        PartnerDto(partner_id="BNK-JPM", name="JPMorgan Chase", bic="CHASUS33", role="prime-broker", status="active", home="US-East", supported_pairs=["EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF"], cutoff_utc="21:00"),
        PartnerDto(partner_id="BNK-HSBC", name="HSBC", bic="HSBCGB2L", role="correspondent", status="active", home="Ireland", supported_pairs=["EUR/USD", "GBP/USD", "EUR/GBP", "USD/SGD"], cutoff_utc="16:00"),
        PartnerDto(partner_id="BNK-DB", name="Deutsche Bank", bic="DEUTDEFF", role="prime-broker", status="active", home="France", supported_pairs=["EUR/USD", "EUR/GBP", "EUR/JPY", "USD/CHF"], cutoff_utc="16:00"),
        PartnerDto(partner_id="BNK-CITI", name="Citi", bic="CITIUS33", role="clearer", status="active", home="US-East", supported_pairs=["EUR/USD", "USD/JPY", "AUD/USD", "USD/CAD"], cutoff_utc="21:00"),
        PartnerDto(partner_id="BNK-BARC", name="Barclays", bic="BARCGB22", role="correspondent", status="active", home="Ireland", supported_pairs=["GBP/USD", "EUR/GBP", "EUR/USD"], cutoff_utc="16:00"),
        PartnerDto(partner_id="BNK-SC", name="Standard Chartered", bic="SCBLSGSG", role="correspondent", status="active", home="Singapore", supported_pairs=["USD/SGD", "USD/INR", "USD/JPY", "AUD/USD"], cutoff_utc="09:00"),
        PartnerDto(partner_id="BNK-BNP", name="BNP Paribas", bic="BNPAFRPP", role="prime-broker", status="active", home="France", supported_pairs=["EUR/USD", "EUR/GBP", "EUR/JPY"], cutoff_utc="16:00"),
        PartnerDto(partner_id="BNK-MUFG", name="MUFG", bic="BOTKJPJT", role="correspondent", status="active", home="Japan", supported_pairs=["USD/JPY", "EUR/JPY", "USD/KRW"], cutoff_utc="07:00"),
    ]

    def find_partners(self, request: ListPartnersRequest) -> PartnerRowsDto:
        rows = PartnerDaoImpl._partners
        if request.role:
            rows = [row for row in rows if row.role == request.role]
        if request.pair:
            rows = [row for row in rows if request.pair in row.supported_pairs]
        return PartnerRowsDto(partners=rows)

    def find_partner(self, request: GetPartnerRequest) -> PartnerRowDto:
        found = next((row for row in PartnerDaoImpl._partners if row.partner_id == request.partner_id), None)
        return PartnerRowDto(partner=found)
