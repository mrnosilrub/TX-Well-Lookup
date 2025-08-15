from __future__ import annotations

from sqlalchemy import Column, Integer, String, Float, Date, text
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class WellReport(Base):
    __tablename__ = "well_reports"

    id = Column(Integer, primary_key=True)
    report_id = Column(String, unique=True, index=True)
    owner_name = Column(String)
    address = Column(String)
    county = Column(String, index=True)
    date_completed = Column(Date)
    depth_ft = Column(Float)
    lat = Column(Float)
    lon = Column(Float)
    location_error_m = Column(Float, server_default=text("0"))
    # geom exists in DB; queries should use ST_DWithin etc. via text() SQL


