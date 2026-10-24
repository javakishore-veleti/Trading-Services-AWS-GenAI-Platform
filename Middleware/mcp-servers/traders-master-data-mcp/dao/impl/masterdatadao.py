from common.dtos.req_resp_dtos import (
    BookChannelDto,
    BookChannelRowsDto,
    BookDefaultDto,
    BookDefaultRowsDto,
    BookDto,
    BookRowsDto,
    ChannelRowsDto,
    CountryDto,
    CountryRowsDto,
    DeskDto,
    DeskRowsDto,
    EmptyRequest,
    InstallationDto,
    InstallationRowsDto,
    ListCountriesRequest,
    ListInstallationsRequest,
    ListTradersRequest,
    TraderDto,
    TraderRowsDto,
)
from dao.interfaces import MasterDataDao


class MasterDataDaoImpl(MasterDataDao):
    _channels: list[str] = ["Advisor", "Partner", "Dealer", "Mobile", "Web", "Kiosk"]
    _countries: list[CountryDto] = [
        CountryDto(code="US-EAST", name="US-East", region="US", compass="east"),
        CountryDto(code="US-WEST", name="US-West", region="US", compass="west"),
        CountryDto(code="US-CENTRAL", name="US-Central", region="US", compass="central"),
        CountryDto(code="US-SOUTH", name="US-South", region="US", compass="south"),
        CountryDto(code="NO", name="Norway", region="Europe", compass="north"),
        CountryDto(code="SE", name="Sweden", region="Europe", compass="north"),
        CountryDto(code="FI", name="Finland", region="Europe", compass="north"),
        CountryDto(code="PL", name="Poland", region="Europe", compass="east"),
        CountryDto(code="RO", name="Romania", region="Europe", compass="east"),
        CountryDto(code="IE", name="Ireland", region="Europe", compass="west"),
        CountryDto(code="FR", name="France", region="Europe", compass="west"),
        CountryDto(code="PT", name="Portugal", region="Europe", compass="west"),
        CountryDto(code="ES", name="Spain", region="Europe", compass="south"),
        CountryDto(code="IT", name="Italy", region="Europe", compass="south"),
        CountryDto(code="MN", name="Mongolia", region="Asia", compass="north"),
        CountryDto(code="KZ", name="Kazakhstan", region="Asia", compass="north"),
        CountryDto(code="JP", name="Japan", region="Asia", compass="east"),
        CountryDto(code="KR", name="South Korea", region="Asia", compass="east"),
        CountryDto(code="TW", name="Taiwan", region="Asia", compass="east"),
        CountryDto(code="IN", name="India", region="Asia", compass="west"),
        CountryDto(code="AE", name="United Arab Emirates", region="Asia", compass="west"),
        CountryDto(code="SG", name="Singapore", region="Asia", compass="south"),
        CountryDto(code="ID", name="Indonesia", region="Asia", compass="south"),
        CountryDto(code="TH", name="Thailand", region="Asia", compass="south"),
    ]
    _desks: list[DeskDto] = [
        DeskDto(desk_id="TD-G10-SPOT", name="G10 Spot"),
        DeskDto(desk_id="TD-G10-FWD", name="G10 Forwards"),
        DeskDto(desk_id="TD-EM", name="Emerging Markets"),
        DeskDto(desk_id="TD-OPTIONS", name="FX Options"),
        DeskDto(desk_id="TD-CORPORATE", name="Corporate Coverage"),
        DeskDto(desk_id="TD-PRIVATE", name="Private Bank"),
    ]
    _installations: list[InstallationDto] = [
        InstallationDto(desk_id="TD-G10-SPOT", country_code="US-EAST", channels=["Dealer", "Web", "Mobile"]),
        InstallationDto(desk_id="TD-G10-SPOT", country_code="US-WEST", channels=["Dealer", "Web"]),
        InstallationDto(desk_id="TD-G10-SPOT", country_code="IE", channels=["Advisor", "Dealer", "Web"]),
        InstallationDto(desk_id="TD-G10-SPOT", country_code="JP", channels=["Dealer", "Mobile"]),
        InstallationDto(desk_id="TD-G10-SPOT", country_code="SG", channels=["Dealer", "Web", "Kiosk"]),
        InstallationDto(desk_id="TD-G10-FWD", country_code="US-CENTRAL", channels=["Advisor", "Dealer"]),
        InstallationDto(desk_id="TD-G10-FWD", country_code="FR", channels=["Advisor", "Dealer", "Partner"]),
        InstallationDto(desk_id="TD-G10-FWD", country_code="NO", channels=["Advisor", "Web"]),
        InstallationDto(desk_id="TD-EM", country_code="SG", channels=["Dealer", "Partner", "Web"]),
        InstallationDto(desk_id="TD-EM", country_code="IN", channels=["Dealer", "Mobile"]),
        InstallationDto(desk_id="TD-EM", country_code="KR", channels=["Dealer", "Web"]),
        InstallationDto(desk_id="TD-EM", country_code="PL", channels=["Advisor", "Dealer"]),
        InstallationDto(desk_id="TD-OPTIONS", country_code="US-EAST", channels=["Dealer", "Advisor"]),
        InstallationDto(desk_id="TD-OPTIONS", country_code="FR", channels=["Dealer"]),
        InstallationDto(desk_id="TD-OPTIONS", country_code="JP", channels=["Dealer", "Advisor"]),
        InstallationDto(desk_id="TD-CORPORATE", country_code="US-SOUTH", channels=["Advisor", "Web", "Mobile"]),
        InstallationDto(desk_id="TD-CORPORATE", country_code="ES", channels=["Advisor", "Partner", "Kiosk"]),
        InstallationDto(desk_id="TD-CORPORATE", country_code="AE", channels=["Advisor", "Partner"]),
        InstallationDto(desk_id="TD-CORPORATE", country_code="TH", channels=["Web", "Kiosk", "Mobile"]),
        InstallationDto(desk_id="TD-PRIVATE", country_code="US-WEST", channels=["Advisor", "Mobile", "Web"]),
        InstallationDto(desk_id="TD-PRIVATE", country_code="IT", channels=["Advisor", "Kiosk"]),
        InstallationDto(desk_id="TD-PRIVATE", country_code="SG", channels=["Advisor", "Mobile"]),
        InstallationDto(desk_id="TD-PRIVATE", country_code="FI", channels=["Advisor", "Web"]),
    ]
    _books: list[BookDto] = [
        BookDto(book_id="BK-G10-SPOT", name="G10 Spot Flow", desk_id="TD-G10-SPOT", base_currency="USD"),
        BookDto(book_id="BK-G10-FWD", name="G10 Forward Flow", desk_id="TD-G10-FWD", base_currency="USD"),
        BookDto(book_id="BK-EM-ASIA", name="Asia EM Flow", desk_id="TD-EM", base_currency="USD"),
        BookDto(book_id="BK-EM-EUROPE", name="Europe EM Flow", desk_id="TD-EM", base_currency="EUR"),
        BookDto(book_id="BK-OPTIONS", name="G10 Options", desk_id="TD-OPTIONS", base_currency="USD"),
        BookDto(book_id="BK-CORPORATE", name="Corporate FX", desk_id="TD-CORPORATE", base_currency="USD"),
    ]
    _defaults: list[BookDefaultDto] = [
        BookDefaultDto(book_id="BK-G10-SPOT", default_channel="Dealer", default_tenor="spot", default_notional=1000000, default_pair="EUR/USD"),
        BookDefaultDto(book_id="BK-G10-FWD", default_channel="Advisor", default_tenor="1M", default_notional=2000000, default_pair="EUR/USD"),
        BookDefaultDto(book_id="BK-EM-ASIA", default_channel="Dealer", default_tenor="1M", default_notional=500000, default_pair="USD/SGD"),
        BookDefaultDto(book_id="BK-EM-EUROPE", default_channel="Advisor", default_tenor="1M", default_notional=500000, default_pair="EUR/USD"),
        BookDefaultDto(book_id="BK-OPTIONS", default_channel="Dealer", default_tenor="3M", default_notional=1000000, default_pair="EUR/USD"),
        BookDefaultDto(book_id="BK-CORPORATE", default_channel="Web", default_tenor="spot", default_notional=250000, default_pair="EUR/USD"),
    ]
    _book_channels: list[BookChannelDto] = [
        BookChannelDto(book_id="BK-G10-SPOT", channels=["Dealer", "Web", "Mobile"]),
        BookChannelDto(book_id="BK-G10-FWD", channels=["Advisor", "Dealer", "Partner"]),
        BookChannelDto(book_id="BK-EM-ASIA", channels=["Dealer", "Partner", "Web"]),
        BookChannelDto(book_id="BK-EM-EUROPE", channels=["Advisor", "Dealer"]),
        BookChannelDto(book_id="BK-OPTIONS", channels=["Dealer", "Advisor"]),
        BookChannelDto(book_id="BK-CORPORATE", channels=["Advisor", "Web", "Mobile", "Kiosk", "Partner"]),
    ]
    _traders: list[TraderDto] = [
        TraderDto(trader_id="TR-01", name="Helen Cho", desk_id="TD-G10-SPOT", book_id="BK-G10-SPOT", location="US-EAST"),
        TraderDto(trader_id="TR-02", name="Marcus Hale", desk_id="TD-G10-SPOT", book_id="BK-G10-SPOT", location="IE"),
        TraderDto(trader_id="TR-03", name="Aiko Sato", desk_id="TD-G10-SPOT", book_id="BK-G10-SPOT", location="JP"),
        TraderDto(trader_id="TR-04", name="Claire Dubois", desk_id="TD-G10-FWD", book_id="BK-G10-FWD", location="FR"),
        TraderDto(trader_id="TR-05", name="Lars Nilsen", desk_id="TD-G10-FWD", book_id="BK-G10-FWD", location="NO"),
        TraderDto(trader_id="TR-06", name="Priya Shah", desk_id="TD-EM", book_id="BK-EM-ASIA", location="SG"),
        TraderDto(trader_id="TR-07", name="Min-jun Park", desk_id="TD-EM", book_id="BK-EM-ASIA", location="KR"),
        TraderDto(trader_id="TR-08", name="Elena Kowalska", desk_id="TD-EM", book_id="BK-EM-EUROPE", location="PL"),
        TraderDto(trader_id="TR-09", name="James Okonkwo", desk_id="TD-OPTIONS", book_id="BK-OPTIONS", location="US-EAST"),
        TraderDto(trader_id="TR-10", name="Sofia Rossi", desk_id="TD-PRIVATE", book_id="BK-CORPORATE", location="IT"),
        TraderDto(trader_id="TR-11", name="Noah Bennett", desk_id="TD-CORPORATE", book_id="BK-CORPORATE", location="US-SOUTH"),
        TraderDto(trader_id="TR-12", name="Fatima Al Najjar", desk_id="TD-CORPORATE", book_id="BK-CORPORATE", location="AE"),
    ]

    def find_channels(self, request: EmptyRequest) -> ChannelRowsDto:
        return ChannelRowsDto(channels=list(MasterDataDaoImpl._channels))

    def find_countries(self, request: ListCountriesRequest) -> CountryRowsDto:
        rows = MasterDataDaoImpl._countries
        if request.region:
            rows = [row for row in rows if row.region == request.region]
        return CountryRowsDto(countries=rows)

    def find_desks(self, request: EmptyRequest) -> DeskRowsDto:
        return DeskRowsDto(desks=list(MasterDataDaoImpl._desks))

    def find_installations(self, request: ListInstallationsRequest) -> InstallationRowsDto:
        rows = MasterDataDaoImpl._installations
        if request.desk_id:
            rows = [row for row in rows if row.desk_id == request.desk_id]
        if request.country_code:
            rows = [row for row in rows if row.country_code == request.country_code]
        return InstallationRowsDto(installations=rows)

    def find_books(self, request: EmptyRequest) -> BookRowsDto:
        return BookRowsDto(books=list(MasterDataDaoImpl._books))

    def find_book_defaults(self, request: EmptyRequest) -> BookDefaultRowsDto:
        return BookDefaultRowsDto(defaults=list(MasterDataDaoImpl._defaults))

    def find_book_channels(self, request: EmptyRequest) -> BookChannelRowsDto:
        return BookChannelRowsDto(book_channels=list(MasterDataDaoImpl._book_channels))

    def find_traders(self, request: ListTradersRequest) -> TraderRowsDto:
        rows = MasterDataDaoImpl._traders
        if request.desk_id:
            rows = [row for row in rows if row.desk_id == request.desk_id]
        return TraderRowsDto(traders=rows)
