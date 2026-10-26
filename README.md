# 🇮🇳 RideConnect India — Pan-India Ride-Hailing, Scheduled Trips & Logistics Platform

A web-first, full-stack ride-hailing and courier parcel delivery platform built for **all over India**, spanning all 28 States and 8 Union Territories with support for 50+ major cities.

---

## 🌟 Key Highlights & Specific Features

### 1. 🇮🇳 Pan-India Geographical Scope (Requirement 18 Expanded)
- **Nationwide Coverage:** Bounded coordinate registries, landmarks, and airports across all zones:
  - **North:** Delhi NCR, Chandigarh, Jaipur, Lucknow, Amritsar, Dehradun
  - **West:** Mumbai Metropolitan, Pune, Ahmedabad, Surat, Goa
  - **South:** Bengaluru, Hyderabad, Chennai, Kochi, Coimbatore
  - **East & Central:** Kolkata, Indore, Bhopal, Patna, Bhubaneswar, Guwahati
- **Intercity Outstation Highway Corridors:** Pre-configured routes (e.g. Mumbai ➔ Pune, Delhi ➔ Agra, Bengaluru ➔ Mysuru, Indore ➔ Ujjain) with estimated highway distance and Fastag toll calculations.

### 2. 🚗 Multi-Vehicle Categories for Indian Realities
- 🛵 **Moto / Bike Taxi:** Solo quick commuter for dense urban traffic (Base ₹20 + ₹7/km).
- 🛺 **Auto-Rickshaw:** Classic Indian 3-wheeler (Base ₹25 + ₹9.5/km).
- 🚗 **Mini Cab:** Pocket-friendly AC compact hatchback (Base ₹40 + ₹12/km).
- 🚘 **Prime Sedan:** Spacious comfortable family sedan (Base ₹60 + ₹15/km).
- 🚙 **SUV / XL:** 6-seater Innova/Ertiga for large groups & airport luggage (Base ₹85 + ₹19/km).
- 🛣️ **Highway Outstation:** Dedicated long-distance vehicles with verified highway captains.

### 3. 📅 Advance Scheduled Rides (Requirement 16)
- Book rides up to **7 days in advance**.
- Modification supported up to 2 hours before pickup.
- **Cancellation Policy:** Free cancellation >1 hour prior to pickup; ₹30 cancellation penalty if cancelled within 1 hour.

### 4. 📦 P2P Parcel Courier Delivery (Requirement 17)
- 3 Size Tiers:
  - **Small (Up to 5 kg):** Documents, keys, food, apparel (Base ₹40 + ₹8/km).
  - **Medium (5 to 15 kg):** Electronics, cartons, boxes (Base ₹60 + ₹10/km).
  - **Large (15 to 30 kg):** Luggage, heavy cartons (Base ₹80 + ₹12/km).
- Weight limit enforced strictly at **30 kg max**.
- **Proof of Pickup:** Driver uploads parcel photo confirmation.
- **Proof of Delivery:** Recipient digital signature and delivery OTP verification.

### 5. 🚨 Safety & 24x7 Emergency SOS (Requirement 11)
- 1-Click Red SOS button instantly accessible across all screens.
- **National Emergency (112 ERSS)**, **Police (100)**, and **Women Helpline (1091)** escalation protocol.
- Automated SMS / WhatsApp live GPS tracking broadcast to family contacts.
- 4-digit security PIN to prevent vehicle misidentification.

### 6. 💳 Indian Payments & GST Tax Invoicing (Requirement 6)
- **UPI Integration:** Dynamic UPI QR Code Intent generator compatible with PhonePe, Google Pay, Paytm, BHIM, Cred.
- Cards (RuPay, Visa, Mastercard), Net Banking, and Cash to Driver.
- **Compliant GST Tax Receipts:** HSN/SAC code `996412`, 5% Transport GST breakdown (2.5% CGST + 2.5% SGST).

---

## 🚀 Quick Start Guide

### 1. Start the Server
```powershell
python run_server.py
```

### 2. Access Web Portals
- **Master Landing & Showcase:** [http://localhost:8000/web/index.html](http://localhost:8000/web/index.html)
- **Rider Portal:** [http://localhost:8000/web/rider.html](http://localhost:8000/web/rider.html)
- **Driver Partner Dashboard:** [http://localhost:8000/web/driver.html](http://localhost:8000/web/driver.html)
- **Pan-India Control Center:** [http://localhost:8000/web/admin.html](http://localhost:8000/web/admin.html)
- **FastAPI Interactive Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. Run Automated Tests
```powershell
python test_runner.py
```

---

## 🔑 Pre-Seeded 1-Click Test Credentials

| Role | Name | Phone Number | Password | City / Base |
| :--- | :--- | :--- | :--- | :--- |
| **Rider** | Aarav Patel | `+91 98765 43210` | `riderpassword123` | Mumbai |
| **Driver** | Vikram Singh Gurjar | `+91 98111 22334` | `driverpassword123` | Delhi NCR (Maruti Dzire: `DL 01 AZ 4521`) |
| **Admin** | Rajesh Sharma | `+91 98765 00001` | `adminpassword123` | National Operations Dispatcher |
