import os
import glob
import uuid
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from kerykeion import AstrologicalSubject, KerykeionChartSVG
from app.core.config import settings
from app.schemas.shema import AstroRequest, SynastryRequest, TransitRequest


class NatalchartrulerService:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="natalchartruler_client")
        self.tf = TimezoneFinder()
        self.output_dir = settings.BASE_OUTPUT_DIR

    def get_full_report(self, req: AstroRequest):
            location = self.geolocator.geocode(req.city)
            if not location:
                raise ValueError(f"City '{req.city}' not found")

            lat, lng = location.latitude, location.longitude
            tz = self.tf.timezone_at(lng=lng, lat=lat)
            internal_name = f"{req.name}_{uuid.uuid4().hex[:6]}"

            subject = AstrologicalSubject(
                internal_name, req.year, req.month, req.day, req.hour, req.minute,
                city=req.city, lat=lat, lng=lng, tz_str=tz
            )
            
            try:
                subject.houses_system = req.house_system.value
            except:
                pass

            selected_theme = None if req.theme.value == "Classic" else req.theme.value

            chart = KerykeionChartSVG(
                subject, 
                new_output_directory=self.output_dir,
                theme=selected_theme
            )
            chart.makeSVG()

            planets_data = {
                "Sun": {"pos": subject.sun.position, "house": subject.sun.house},
                "Moon": {"pos": subject.moon.position, "house": subject.moon.house},
                "Mercury": {"pos": subject.mercury.position, "house": subject.mercury.house},
                "Venus": {"pos": subject.venus.position, "house": subject.venus.house},
                "Mars": {"pos": subject.mars.position, "house": subject.mars.house},
                "Jupiter": {"pos": subject.jupiter.position, "house": subject.jupiter.house},
                "Saturn": {"pos": subject.saturn.position, "house": subject.saturn.house}
            }

            svg_content = self._extract_svg_and_cleanup(internal_name)

            return {
                "svg": svg_content,
                "data": {
                    "name": req.name,
                    "planets": planets_data,
                    "info": {
                        "lat": lat,
                        "lng": lng,
                        "tz": tz
                    }
                }
            }
    
    def get_transit_report(self, req: TransitRequest):
            location = self.geolocator.geocode(req.person.city)
            if not location:
                print(f"⚠️ Warning: City '{req.person.city}' not found")
                return {"error": "City not found"}

            lat, lng = location.latitude, location.longitude
            tz = self.tf.timezone_at(lng=lng, lat=lat)
            
            internal_name = f"Transit_{req.person.name}_{uuid.uuid4().hex[:6]}"

            subject = AstrologicalSubject(
                internal_name, 
                req.person.year, req.person.month, req.person.day,
                req.person.hour, req.person.minute,
                city=req.person.city, lat=lat, lng=lng, tz_str=tz
            )

            transit_subject = AstrologicalSubject(
                f"T_{internal_name}",
                req.transit_date.year, req.transit_date.month, req.transit_date.day,
                req.transit_date.hour, req.transit_date.minute,
                city=req.person.city, lat=lat, lng=lng, tz_str=tz
            )

            user_theme = req.person.theme.value
            selected_theme = None if user_theme == "Classic" else user_theme

            try:
                chart = KerykeionChartSVG(
                    subject,
                    "Transit", 
                    transit_subject,
                    new_output_directory=self.output_dir,
                    theme=selected_theme
                )
            except Exception as e:
                print(f"⚠️ Falling back to manual attribute assignment due to: {e}")
                chart = KerykeionChartSVG(subject, new_output_directory=self.output_dir, theme=selected_theme)
                chart.chart_type = "Transit"
                chart.t_subject = transit_subject
                chart.second_obj = transit_subject 
                chart.second_subject = transit_subject

            chart.makeSVG()
            svg_content = self._extract_svg_and_cleanup(internal_name)

            return {
                "svg": svg_content,
                "data": {
                    "status": "success", 
                    "transit_date": req.transit_date.isoformat(),
                    "theme_used": user_theme
                }
            }     
            
    def get_synastry_report(self, req: SynastryRequest):
            loc1 = self.geolocator.geocode(req.person_one.city)
            if not loc1: raise ValueError("City 1 not found")
            lat1, lng1 = loc1.latitude, loc1.longitude
            tz1 = self.tf.timezone_at(lng=lng1, lat=lat1)
            
            internal_name = f"Syn_{req.person_one.name}_{uuid.uuid4().hex[:6]}"

            subject1 = AstrologicalSubject(
                internal_name, 
                req.person_one.year, req.person_one.month, req.person_one.day,
                req.person_one.hour, req.person_one.minute,
                city=req.person_one.city, lat=lat1, lng=lng1, tz_str=tz1
            )

            loc2 = self.geolocator.geocode(req.person_two.city)
            if not loc2: raise ValueError("City 2 not found")
            lat2, lng2 = loc2.latitude, loc2.longitude
            tz2 = self.tf.timezone_at(lng=lng2, lat=lat2)
            
            subject2 = AstrologicalSubject(
                f"P2_{internal_name}", 
                req.person_two.year, req.person_two.month, req.person_two.day,
                req.person_two.hour, req.person_two.minute,
                city=req.person_two.city, lat=lat2, lng=lng2, tz_str=tz2
            )

            user_theme = req.person_one.theme.value
            selected_theme = None if user_theme == "Classic" else user_theme

            try:
                chart = KerykeionChartSVG(
                    subject1,
                    "Synastry", 
                    subject2,
                    new_output_directory=self.output_dir,
                    theme=selected_theme
                )
            except Exception as e:
                print(f"⚠️ Synastry fallback: {e}")
                chart = KerykeionChartSVG(subject1, new_output_directory=self.output_dir, theme=selected_theme)
                chart.chart_type = "Synastry"
                chart.second_obj = subject2
                chart.second_subject = subject2

            chart.makeSVG()
            svg_content = self._extract_svg_and_cleanup(internal_name)

            return {
                "svg": svg_content,
                "data": {"status": "success", "p1": req.person_one.name, "p2": req.person_two.name}
            }
        
    def _extract_svg_and_cleanup(self, internal_name: str):
            search_pattern = os.path.join(self.output_dir, f"*{internal_name}*.svg")
            found_files = glob.glob(search_pattern)

            if not found_files:
                print(f"⚠️ Warning: No SVG files found for {internal_name} in {self.output_dir}")
                return None

            target_file = max(found_files, key=os.path.getmtime)
            
            content = None
            try:
                with open(target_file, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                print(f"❌ Error reading SVG: {e}")
                return None
            finally:
                for file_path in found_files:
                    try:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            print(f"🧹 Cleaned up: {file_path}")
                    except Exception as e:
                        print(f"❌ Failed to delete {file_path}: {e}")
            
            return content