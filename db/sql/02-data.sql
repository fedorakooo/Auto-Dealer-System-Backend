INSERT INTO cities (name, country) VALUES
('Warsaw', 'Poland'),
('Krakow', 'Poland'),
('Gdansk', 'Poland'),
('Wroclaw', 'Poland'),
('Poznan', 'Poland'),
('Minsk', 'Belarus'),
('Brest', 'Belarus'),
('Grodno', 'Belarus'),
('Lodz', 'Poland'),
('Katowice', 'Poland'),
('Vitebsk', 'Belarus'),
('Gomel', 'Belarus');

INSERT INTO dealerships (name, address, city_id, phone_number, email, opening_hours, latitude, longitude) VALUES
('Audi Centrum Warsaw', 'ul. Sekundowa 2, 02-173 Warsaw', 1, '+48225737000', 'warszawa@audi-centrum.pl', 'Mon-Sat 09:00-20:00', 52.1937, 20.9479),
('Audi Krakow', 'ul. Zakopiańska 169, 30-435 Krakow', 2, '+48122525252', 'krakow@audi-dealer.pl', 'Mon-Sat 09:00-19:00', 50.0152, 19.9240),
('Audi Centrum Gdansk', 'aleja Grunwaldzka 347, 80-264 Gdansk', 3, '+48585207800', 'gdansk@audi-centrum.pl', 'Mon-Fri 09:00-18:00', 54.3813, 18.5912),
('Audi Minsk', 'pr-t Nezavisimosti 198, Minsk, 220056', 6, '+375173360000', 'minsk@audi.by', 'Mon-Sun 09:00-20:00', 53.9388, 27.6953),
('Audi Brest', 'ul. Moskovskaya 364, Brest, 224023', 7, '+375162550000', 'brest@audi.by', 'Mon-Sat 09:00-19:00', 52.1009, 23.7667),
('Audi Minsk North', 'ul. Kalinovskogo 55, Minsk', 6, '+375173335555', 'minsk-north@audi.by', 'Mon-Sun 09:00-20:00', 53.9465, 27.6338),
('Audi Minsk South', 'pr-t Dzerzhinskogo 125, Minsk', 6, '+375173337777', 'minsk-south@audi.by', 'Mon-Sun 09:00-21:00', 53.8579, 27.4856),
('Audi Lodz', 'ul. Piotrkowska 100, 90-001 Lodz', 9, '+48423678900', 'lodz@audi.pl', 'Mon-Sat 09:00-19:00', 51.7592, 19.4560),
('Audi Katowice', 'ul. 3 Maja 10, 40-001 Katowice', 10, '+48322123456', 'katowice@audi.pl', 'Mon-Sat 09:00-19:00', 50.2649, 19.0238),
('Audi Vitebsk', 'ul. Lenina 15, Vitebsk', 11, '+375212345678', 'vitebsk@audi.by', 'Mon-Sun 09:00-20:00', 55.1904, 30.2049),
('Audi Gomel', 'pr-t Lenina 45, Gomel', 12, '+375232345678', 'gomel@audi.by', 'Mon-Sun 09:00-20:00', 52.4410, 30.9754);

INSERT INTO body_types (name) VALUES
('Sedan'), ('Avant'), ('Sportback'), ('SUV'), ('Coupe'), ('Roadster'), ('Allroad');

INSERT INTO engines (name, engine_code, displacement_cm3, cylinders, horsepower, fuel_type, configuration, induction) VALUES
('35 TFSI', 'EA211 evo', 1498, 4, 150, 'gasoline', 'I4', 'Turbocharged'),
('45 TFSI', 'EA888', 1984, 4, 265, 'gasoline', 'I4', 'Turbocharged'),
('55 TFSI', 'EA839', 2995, 6, 340, 'gasoline', 'V6', 'Turbocharged'),
('40 TDI', 'EA288 evo', 1968, 4, 204, 'diesel', 'I4', 'Turbocharged'),
('50 TDI', 'EA897 evo', 2967, 6, 286, 'diesel', 'V6', 'Turbocharged'),
('e-tron 55 quattro', 'EDU55', NULL, NULL, 408, 'electric', NULL, NULL),
('4.0 TFSI V8', 'EA825', 3996, 8, 600, 'gasoline', 'V8', 'Turbocharged'),
('30 TFSI', 'EA211', 999, 3, 110, 'gasoline', 'I3', 'Turbocharged'),
('60 TDI', 'EA897 evo2', 3956, 8, 435, 'diesel', 'V8', 'Turbocharged'),
('e-tron 50 quattro', 'EDU50', NULL, NULL, 308, 'electric', NULL, NULL);

INSERT INTO transmissions (name, type, number_of_gears) VALUES
('S tronic', 'dct', 7),
('tiptronic', 'automatic', 8),
('6-Speed Manual', 'manual', 6),
('e-tron single-speed', 'automatic', 1),
('7-Speed S tronic', 'dct', 7),
('8-Speed tiptronic', 'automatic', 8);

INSERT INTO features (name, description) VALUES
('Audi virtual cockpit plus', 'Fully digital 12.3-inch instrument cluster.'),
('Matrix LED headlights', 'Adaptive LED headlights with dynamic turn signals.'),
('MMI Navigation plus system', 'Advanced navigation system with MMI touch response display.'),
('quattro drive', 'Legendary permanent all-wheel drive from Audi.'),
('Air suspension', 'Adaptive air suspension system.'),
('Bang & Olufsen Premium Sound System', '3D audio sound system.'),
('S line package', 'Styling S line package.'),
('Parking assistant plus', '360° camera system and automatic parking.'),
('Heads-up Display', 'Projection display on the windshield.'),
('Adaptive Cruise Assist', 'Adaptive cruise control system.'),
('Night Vision Assistant', 'Night vision assistance system.'),
('Rear Seat Entertainment', 'Screens for rear passengers.');

INSERT INTO models (id, body_type_id, engine_id, transmission_id, is_in_production, name, model_code, production_year_start, drive_type, number_of_seats) VALUES
('2bb5382f-462d-42ac-8fb9-f223d0261941', 1, 2, 1, true, 'A4 Sedan 45 TFSI', '8W', 2023, 'AWD', 5),
('a223bd5f-1376-4f30-94a4-9d49d6f447fc', 4, 5, 2, true, 'Q7 50 TDI', '4M', 2022, 'AWD', 7),
('f13b6a52-aec2-4e00-b416-c155e1860250', 3, 3, 1, true, 'A5 Sportback 55 TFSI', 'F5', 2024, 'AWD', 5),
('89ccc9a3-76b1-4cc9-aa49-b73dea7ecf9f', 4, 6, 4, true, 'Q8 e-tron', 'GE', 2023, 'AWD', 5),
('96981369-c44b-4e82-906e-db970a77ea88', 2, 4, 1, true, 'A6 Avant 40 TDI', '4K', 2023, 'FWD', 5),
('d3ab44e9-e2ce-486d-89b5-2f8cf160aaaf', 3, 1, 1, true, 'A3 Sportback 35 TFSI', '8Y', 2024, 'FWD', 5),
('19def3bc-4d70-44fe-944b-ad3cf09c8184', 3, 7, 2, true, 'RS 6 Avant', '4K', 2024, 'AWD', 5),
('aa0f7b44-25c8-4ad0-843d-6b46e18f91ee', 1, 8, 5, true, 'A3 Sedan 30 TFSI', '8Y', 2024, 'FWD', 5),
('3b7a6af5-918e-4eb3-99d1-c4f56f25f01f', 4, 9, 2, true, 'Q8 60 TDI', '4M', 2023, 'AWD', 7),
('6d6e9549-c8de-47e5-9dfb-1f5e00a7e9cd', 3, 2, 1, true, 'A5 Sportback 50 TFSI', 'F5', 2025, 'AWD', 5),
('caa83b09-cf89-4a0d-98a9-b18fd73cfdd7', 4, 10, 4, true, 'Q4 e-tron 50', 'GE', 2023, 'AWD', 5);

INSERT INTO model_features (model_id, feature_id) VALUES
('2bb5382f-462d-42ac-8fb9-f223d0261941', 1),
('2bb5382f-462d-42ac-8fb9-f223d0261941', 2),
('a223bd5f-1376-4f30-94a4-9d49d6f447fc', 3),
('a223bd5f-1376-4f30-94a4-9d49d6f447fc', 4),
('f13b6a52-aec2-4e00-b416-c155e1860250', 1),
('f13b6a52-aec2-4e00-b416-c155e1860250', 5),
('89ccc9a3-76b1-4cc9-aa49-b73dea7ecf9f', 6),
('89ccc9a3-76b1-4cc9-aa49-b73dea7ecf9f', 10),
('aa0f7b44-25c8-4ad0-843d-6b46e18f91ee', 1),
('aa0f7b44-25c8-4ad0-843d-6b46e18f91ee', 2),
('3b7a6af5-918e-4eb3-99d1-c4f56f25f01f', 3),
('3b7a6af5-918e-4eb3-99d1-c4f56f25f01f', 4),
('6d6e9549-c8de-47e5-9dfb-1f5e00a7e9cd', 1),
('6d6e9549-c8de-47e5-9dfb-1f5e00a7e9cd', 2);

INSERT INTO vehicles (model_id, dealership_id, vin, production_year, exterior_color, interior_color, price, is_active) VALUES
('2bb5382f-462d-42ac-8fb9-f223d0261941', 1, 'WAUZZZ8WXP000001', 2023, 'Daytona Gray', 'Black', 45000.00, true),
('a223bd5f-1376-4f30-94a4-9d49d6f447fc', 2, 'WAUZZZ4MXN000002', 2022, 'Glacier White', 'Brown', 80000.00, true),
('f13b6a52-aec2-4e00-b416-c155e1860250', 3, 'WAUZZZF5XP000003', 2024, 'Tango Red', 'Black', 55000.00, true),
('89ccc9a3-76b1-4cc9-aa49-b73dea7ecf9f', 4, 'WAUZZZGEYP000004', 2023, 'Plasma Blue', 'Gray', 90000.00, true),
('96981369-c44b-4e82-906e-db970a77ea88', 1, 'WAUZZZ4KXP000005', 2023, 'Mythos Black', 'Beige', 60000.00, true),
('d3ab44e9-e2ce-486d-89b5-2f8cf160aaaf', 8, 'WAUZZZ8YXP1000009', 2024, 'Ibis White', 'Black', 35000.00, true),
('3b7a6af5-918e-4eb3-99d1-c4f56f25f01f', 9, 'WAUZZZ4MXN1000010', 2023, 'Daytona Gray', 'Black', 95000.00, true),
('6d6e9549-c8de-47e5-9dfb-1f5e00a7e9cd', 1, 'WAUZZZF5XP1000011', 2025, 'Arrow Grey', 'Black', 60000.00, true),
('caa83b09-cf89-4a0d-98a9-b18fd73cfdd7', 4, 'WAUZZZGEXR1000012', 2023, 'Plasma Blue', 'Black', 70000.00, true),
('2bb5382f-462d-42ac-8fb9-f223d0261941', 6, 'WAUZZZ8WXMINSK01', 2024, 'Mythos Black', 'Brown', 46000.00, true),
('89ccc9a3-76b1-4cc9-aa49-b73dea7ecf9f', 7, 'WAUZZZGEYMINSK02', 2024, 'Daytona Gray', 'Gray', 92000.00, true);
