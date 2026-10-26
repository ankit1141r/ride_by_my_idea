/**
 * Pan-India Cities, Coordinates, Landmarks & Vehicles Registry.
 * Powers client-side geocoding, dropdowns, and map zoom animations.
 */
const INDIA_CITIES = {
  delhi: {
    id: "delhi",
    name: "Delhi NCR",
    state: "Delhi / Haryana / UP",
    region: "North",
    lat: 28.6139,
    lon: 77.2090,
    zoom: 12,
    landmarks: [
      { name: "Indira Gandhi International Airport (IGI)", lat: 28.5562, lon: 77.1000 },
      { name: "New Delhi Railway Station (NDLS)", lat: 28.6430, lon: 77.2197 },
      { name: "Connaught Place (CP), Central Delhi", lat: 28.6315, lon: 77.2167 },
      { name: "Cyber Hub, Gurugram", lat: 28.4986, lon: 77.0895 },
      { name: "Sector 18 Market, Noida", lat: 28.5708, lon: 77.3260 },
      { name: "India Gate & Kartavya Path", lat: 28.6129, lon: 77.2295 }
    ]
  },
  mumbai: {
    id: "mumbai",
    name: "Mumbai Metropolitan",
    state: "Maharashtra",
    region: "West",
    lat: 19.0760,
    lon: 72.8777,
    zoom: 12,
    landmarks: [
      { name: "Chhatrapati Shivaji Maharaj Airport (BOM T2)", lat: 19.0968, lon: 72.8747 },
      { name: "CSMT Railway Terminus", lat: 18.9401, lon: 72.8354 },
      { name: "Bandra-Kurla Complex (BKC)", lat: 19.0664, lon: 72.8687 },
      { name: "Marine Drive & Nariman Point", lat: 18.9438, lon: 72.8234 },
      { name: "Powai Hiranandani Tech Zone", lat: 19.1176, lon: 72.9060 }
    ]
  },
  bengaluru: {
    id: "bengaluru",
    name: "Bengaluru (Bangalore)",
    state: "Karnataka",
    region: "South",
    lat: 12.9716,
    lon: 77.5946,
    zoom: 12,
    landmarks: [
      { name: "Kempegowda International Airport (BLR)", lat: 13.1986, lon: 77.7066 },
      { name: "KSR Bengaluru (Majestic Station)", lat: 12.9781, lon: 77.5695 },
      { name: "Electronic City Phase 1", lat: 12.8452, lon: 77.6602 },
      { name: "Whitefield ITPL", lat: 12.9863, lon: 77.7314 },
      { name: "Koramangala Sony World Signal", lat: 12.9345, lon: 77.6265 }
    ]
  },
  hyderabad: {
    id: "hyderabad",
    name: "Hyderabad",
    state: "Telangana",
    region: "South",
    lat: 17.3850,
    lon: 78.4867,
    zoom: 12,
    landmarks: [
      { name: "Rajiv Gandhi International Airport (HYD)", lat: 17.2403, lon: 78.4294 },
      { name: "Secunderabad Railway Station", lat: 17.4344, lon: 78.5015 },
      { name: "HITEC City / Cyber Towers", lat: 17.4504, lon: 78.3808 },
      { name: "Gachibowli Financial District", lat: 17.4208, lon: 78.3489 },
      { name: "Charminar Monument", lat: 17.3616, lon: 78.4747 }
    ]
  },
  indore: {
    id: "indore",
    name: "Indore",
    state: "Madhya Pradesh",
    region: "Central",
    lat: 22.7196,
    lon: 75.8577,
    zoom: 13,
    landmarks: [
      { name: "Devi Ahilya Bai Holkar Airport (IDR)", lat: 22.7230, lon: 75.8052 },
      { name: "Indore Junction Railway Station", lat: 22.7177, lon: 75.8682 },
      { name: "Rajwada Palace & Sarafa", lat: 22.7187, lon: 75.8542 },
      { name: "Vijay Nagar (Scheme 54)", lat: 22.7533, lon: 75.8937 },
      { name: "Super Corridor TCS/Infosys Campus", lat: 22.7758, lon: 75.8242 },
      { name: "Chappan Dukan Street", lat: 22.7253, lon: 75.8790 }
    ]
  },
  chennai: {
    id: "chennai",
    name: "Chennai",
    state: "Tamil Nadu",
    region: "South",
    lat: 13.0827,
    lon: 80.2707,
    zoom: 12,
    landmarks: [
      { name: "Chennai International Airport (MAA)", lat: 12.9941, lon: 80.1709 },
      { name: "Chennai Central Station (MGR)", lat: 13.0823, lon: 80.2755 },
      { name: "OMR IT Corridor (Tidel Park)", lat: 12.9165, lon: 80.2285 },
      { name: "T. Nagar Commercial Hub", lat: 13.0418, lon: 80.2341 }
    ]
  },
  kolkata: {
    id: "kolkata",
    name: "Kolkata",
    state: "West Bengal",
    region: "East",
    lat: 22.5726,
    lon: 88.3639,
    zoom: 12,
    landmarks: [
      { name: "Netaji Subhash Chandra Bose Airport (CCU)", lat: 22.6547, lon: 88.4467 },
      { name: "Howrah Railway Station", lat: 22.5857, lon: 88.3426 },
      { name: "Salt Lake Sector V (IT Hub)", lat: 22.5760, lon: 88.4338 },
      { name: "Park Street & Victoria Memorial", lat: 22.5518, lon: 88.3516 }
    ]
  },
  pune: {
    id: "pune",
    name: "Pune",
    state: "Maharashtra",
    region: "West",
    lat: 18.5204,
    lon: 73.8567,
    zoom: 12,
    landmarks: [
      { name: "Pune International Airport (PNQ)", lat: 18.5822, lon: 73.9197 },
      { name: "Pune Junction Railway Station", lat: 18.5284, lon: 73.8743 },
      { name: "Hinjawadi IT Park Phase 1", lat: 18.5913, lon: 73.7389 },
      { name: "Koregaon Park (North Main Rd)", lat: 18.5362, lon: 73.8940 }
    ]
  },
  ahmedabad: {
    id: "ahmedabad",
    name: "Ahmedabad & Gandhinagar",
    state: "Gujarat",
    region: "West",
    lat: 23.0225,
    lon: 72.5714,
    zoom: 12,
    landmarks: [
      { name: "Sardar Vallabhbhai Patel Airport (AMD)", lat: 23.0772, lon: 72.6347 },
      { name: "SG Highway / Prahlad Nagar", lat: 23.0125, lon: 72.5074 },
      { name: "GIFT City Gandhinagar", lat: 23.1610, lon: 72.6840 },
      { name: "Sabarmati Riverfront", lat: 23.0366, lon: 72.5739 }
    ]
  },
  jaipur: {
    id: "jaipur",
    name: "Jaipur",
    state: "Rajasthan",
    region: "North",
    lat: 26.9124,
    lon: 75.7873,
    zoom: 12,
    landmarks: [
      { name: "Jaipur International Airport (JAI)", lat: 26.8289, lon: 75.8056 },
      { name: "Jaipur Junction Railway Station", lat: 26.9196, lon: 75.7878 },
      { name: "Hawa Mahal & Johari Bazaar", lat: 26.9239, lon: 75.8267 },
      { name: "World Trade Park (WTP) Malviya Nagar", lat: 26.8533, lon: 75.8050 }
    ]
  },
  lucknow: {
    id: "lucknow",
    name: "Lucknow",
    state: "Uttar Pradesh",
    region: "North",
    lat: 26.8467,
    lon: 80.9462,
    zoom: 12,
    landmarks: [
      { name: "Chaudhary Charan Singh Airport (LKO)", lat: 26.7606, lon: 80.8893 },
      { name: "Charbagh Railway Station", lat: 26.8322, lon: 80.9234 },
      { name: "Hazratganj Market", lat: 26.8525, lon: 80.9455 },
      { name: "Gomti Nagar Vibhuti Khand", lat: 26.8643, lon: 80.9984 }
    ]
  },
  chandigarh: {
    id: "chandigarh",
    name: "Chandigarh Tricity",
    state: "Punjab / Haryana",
    region: "North",
    lat: 30.7333,
    lon: 76.7794,
    zoom: 12,
    landmarks: [
      { name: "Shaheed Bhagat Singh Airport (IXC)", lat: 30.6735, lon: 76.7885 },
      { name: "Sector 17 Plaza", lat: 30.7398, lon: 76.7827 },
      { name: "Sukhna Lake", lat: 30.7421, lon: 76.8188 },
      { name: "IT Park DLF Infocity", lat: 30.7258, lon: 76.8458 }
    ]
  },
  bhopal: {
    id: "bhopal",
    name: "Bhopal",
    state: "Madhya Pradesh",
    region: "Central",
    lat: 23.2599,
    lon: 77.4126,
    zoom: 12,
    landmarks: [
      { name: "Raja Bhoj Airport (BHO)", lat: 23.2875, lon: 77.3378 },
      { name: "Rani Kamlapati Station (RKMP)", lat: 23.2045, lon: 77.4414 },
      { name: "VIP Road & Upper Lake", lat: 23.2500, lon: 77.3800 },
      { name: "MP Nagar Zone 1", lat: 23.2325, lon: 77.4332 }
    ]
  },
  kochi: {
    id: "kochi",
    name: "Kochi (Cochin)",
    state: "Kerala",
    region: "South",
    lat: 9.9312,
    lon: 76.2673,
    zoom: 12,
    landmarks: [
      { name: "Cochin International Airport (COK)", lat: 10.1518, lon: 76.3930 },
      { name: "Lulu International Mall, Edappally", lat: 10.0279, lon: 76.3080 },
      { name: "Infopark Kakkanad", lat: 10.0108, lon: 76.3638 }
    ]
  },
  patna: {
    id: "patna",
    name: "Patna",
    state: "Bihar",
    region: "East",
    lat: 25.5941,
    lon: 85.1376,
    zoom: 12,
    landmarks: [
      { name: "Jay Prakash Narayan Airport (PAT)", lat: 25.5913, lon: 85.0880 },
      { name: "Patna Junction Railway Station", lat: 25.6025, lon: 85.1376 },
      { name: "Dak Bunglow Crossing", lat: 25.6072, lon: 85.1360 }
    ]
  },
  goa: {
    id: "goa",
    name: "Goa (North & South)",
    state: "Goa",
    region: "West",
    lat: 15.4989,
    lon: 73.8278,
    zoom: 11,
    landmarks: [
      { name: "Manohar International Airport (MOPA GOX)", lat: 15.7483, lon: 73.8677 },
      { name: "Dabolim Airport (GOI)", lat: 15.3808, lon: 73.8313 },
      { name: "Calangute & Baga Beach Hub", lat: 15.5439, lon: 73.7553 },
      { name: "Panaji Church Square", lat: 15.4989, lon: 73.8278 }
    ]
  }
};

const VEHICLE_TYPES = [
  { id: "bike", name: "Bike Taxi", icon: "fa-motorcycle", desc: "Fastest solo ride", base: 20, km: 7, min: 25, cap: 1 },
  { id: "auto", name: "Auto-Rickshaw", icon: "fa-bus-simple", desc: "Classic 3-wheeler", base: 25, km: 9.5, min: 30, cap: 3 },
  { id: "mini", name: "Mini Cab", icon: "fa-car-side", desc: "Pocket AC hatchback", base: 40, km: 12, min: 50, cap: 4 },
  { id: "sedan", name: "Prime Sedan", icon: "fa-car", desc: "Spacious & comfortable", base: 60, km: 15, min: 80, cap: 4 },
  { id: "suv", name: "SUV / XL", icon: "fa-van-shuttle", desc: "6-seater Innova/Ertiga", base: 85, km: 19, min: 120, cap: 6 },
  { id: "outstation", name: "Outstation", icon: "fa-route", desc: "Highway intercity", base: 150, km: 13, min: 500, cap: 4 }
];

window.INDIA_CITIES = INDIA_CITIES;
window.VEHICLE_TYPES = VEHICLE_TYPES;
