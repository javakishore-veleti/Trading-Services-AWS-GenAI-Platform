from common.dtos.req_resp_dtos import AnalyticDto, AnalyticRowsDto, GrainRowsDto, ListGrainsRequest, ReadAnalyticsRequest
from dao.interfaces import AnalyticsDao


class AnalyticsDaoImpl(AnalyticsDao):
    _grains: list[str] = ["eod", "intraday", "hourly"]
    _rows: list[AnalyticDto] = [
        AnalyticDto(grain="eod", as_of="2026-10-23", book_id="BK-G10-SPOT", desk_id="TD-G10-SPOT", channel="Dealer", country_code="US-EAST", trade_count=420, volume_usd=860000000, pnl_usd=410000),
        AnalyticDto(grain="eod", as_of="2026-10-23", book_id="BK-G10-SPOT", desk_id="TD-G10-SPOT", channel="Web", country_code="SG", trade_count=188, volume_usd=94000000, pnl_usd=62000),
        AnalyticDto(grain="eod", as_of="2026-10-23", book_id="BK-G10-FWD", desk_id="TD-G10-FWD", channel="Advisor", country_code="FR", trade_count=76, volume_usd=210000000, pnl_usd=155000),
        AnalyticDto(grain="eod", as_of="2026-10-23", book_id="BK-EM-ASIA", desk_id="TD-EM", channel="Dealer", country_code="JP", trade_count=134, volume_usd=175000000, pnl_usd=98000),
        AnalyticDto(grain="eod", as_of="2026-10-23", book_id="BK-EM-EUROPE", desk_id="TD-EM", channel="Advisor", country_code="PL", trade_count=41, volume_usd=38000000, pnl_usd=21000),
        AnalyticDto(grain="eod", as_of="2026-10-23", book_id="BK-OPTIONS", desk_id="TD-OPTIONS", channel="Dealer", country_code="US-EAST", trade_count=29, volume_usd=120000000, pnl_usd=240000),
        AnalyticDto(grain="eod", as_of="2026-10-23", book_id="BK-CORPORATE", desk_id="TD-CORPORATE", channel="Web", country_code="US-SOUTH", trade_count=260, volume_usd=64000000, pnl_usd=33000),
        AnalyticDto(grain="eod", as_of="2026-10-23", book_id="BK-CORPORATE", desk_id="TD-CORPORATE", channel="Kiosk", country_code="ES", trade_count=54, volume_usd=7000000, pnl_usd=4000),
        AnalyticDto(grain="intraday", as_of="2026-10-24T15:00:00Z", book_id="BK-G10-SPOT", desk_id="TD-G10-SPOT", channel="Dealer", country_code="US-EAST", trade_count=96, volume_usd=140000000, pnl_usd=52000),
        AnalyticDto(grain="intraday", as_of="2026-10-24T15:00:00Z", book_id="BK-EM-ASIA", desk_id="TD-EM", channel="Web", country_code="SG", trade_count=40, volume_usd=22000000, pnl_usd=8000),
        AnalyticDto(grain="intraday", as_of="2026-10-24T15:00:00Z", book_id="BK-CORPORATE", desk_id="TD-CORPORATE", channel="Mobile", country_code="TH", trade_count=33, volume_usd=4100000, pnl_usd=900),
        AnalyticDto(grain="hourly", as_of="2026-10-24T16:00:00Z", book_id="BK-G10-SPOT", desk_id="TD-G10-SPOT", channel="Mobile", country_code="JP", trade_count=14, volume_usd=9000000, pnl_usd=2100),
        AnalyticDto(grain="hourly", as_of="2026-10-24T16:00:00Z", book_id="BK-G10-FWD", desk_id="TD-G10-FWD", channel="Partner", country_code="FR", trade_count=6, volume_usd=18000000, pnl_usd=6400),
        AnalyticDto(grain="hourly", as_of="2026-10-24T16:00:00Z", book_id="BK-OPTIONS", desk_id="TD-OPTIONS", channel="Advisor", country_code="US-EAST", trade_count=3, volume_usd=11000000, pnl_usd=15000),
        AnalyticDto(grain="hourly", as_of="2026-10-24T16:00:00Z", book_id="BK-CORPORATE", desk_id="TD-CORPORATE", channel="Web", country_code="AE", trade_count=11, volume_usd=2600000, pnl_usd=700),
    ]

    def find_grains(self, request: ListGrainsRequest) -> GrainRowsDto:
        return GrainRowsDto(grains=list(AnalyticsDaoImpl._grains))

    def find_rows(self, request: ReadAnalyticsRequest) -> AnalyticRowsDto:
        rows = [row for row in AnalyticsDaoImpl._rows if row.grain == request.grain]
        if request.book_id:
            rows = [row for row in rows if row.book_id == request.book_id]
        if request.channel:
            rows = [row for row in rows if row.channel == request.channel]
        if request.country_code:
            rows = [row for row in rows if row.country_code == request.country_code]
        return AnalyticRowsDto(rows=rows)
