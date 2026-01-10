-- Datenbank für "Für eine leckere Zukunft"

-- 1. Users Tabelle
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(250) NOT NULL UNIQUE,
    password VARCHAR(250) NOT NULL
);

-- 2. Todos Tabelle
CREATE TABLE todos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    content VARCHAR(100),
    due DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 3. Recipes Tabelle
CREATE TABLE recipes (
  recipe_id INT AUTO_INCREMENT PRIMARY KEY,
  recipe_name VARCHAR(100),
  recipe_photo VARCHAR(200),
  recipe_instruction VARCHAR(4000),
  recipe_mengenangaben VARCHAR(15),
  recipes_ingredient INT(15)
);

-- 4. Ingredients Tabelle
CREATE TABLE ingredient (
   id INT AUTO_INCREMENT PRIMARY KEY,
   ingredient_name VARCHAR(100),
   vegetarisch BOOLEAN,
   vegan BOOLEAN,
   laktose BOOLEAN,
   ingredient_glutenfrei BOOLEAN
);

-- 5. Improved Liked Tabelle (mit User-Verbindung)
CREATE TABLE liked (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    recipe_id INT NOT NULL,
    liked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id),
    UNIQUE KEY unique_like (user_id, recipe_id)
);

-- =============================================
-- INSERT Statements für Ingredients der 5 Rezepte
-- =============================================

-- Ingredients für Hörnli-Auflauf (Rezept 1)
INSERT INTO ingredient (id, ingredient_name, vegetarisch, vegan, laktose, ingredient_glutenfrei) VALUES
(1, 'Hörnli', TRUE, TRUE, TRUE, FALSE),
(2, 'Käse (gerieben)', TRUE, FALSE, FALSE, TRUE),
(3, 'Schinken', FALSE, FALSE, TRUE, TRUE),
(4, 'Eier', TRUE, FALSE, TRUE, TRUE),
(5, 'Milch', TRUE, FALSE, FALSE, TRUE),
(6, 'Butter', TRUE, FALSE, FALSE, TRUE),
(7, 'Salz', TRUE, TRUE, TRUE, TRUE),
(8, 'Pfeffer', TRUE, TRUE, TRUE, TRUE),
(9, 'Muskatnuss', TRUE, TRUE, TRUE, TRUE);

-- Ingredients für Bananen Pancakes (Rezept 2)
INSERT INTO ingredient (id, ingredient_name, vegetarisch, vegan, laktose, ingredient_glutenfrei) VALUES
(10, 'Bananen', TRUE, TRUE, TRUE, TRUE),
(11, 'Eier', TRUE, FALSE, TRUE, TRUE),
(12, 'Mehl', TRUE, TRUE, TRUE, FALSE),
(13, 'Backpulver', TRUE, TRUE, TRUE, TRUE),
(14, 'Zimt', TRUE, TRUE, TRUE, TRUE),
(15, 'Milch', TRUE, FALSE, FALSE, TRUE),
(16, 'Ahornsirup', TRUE, TRUE, TRUE, TRUE),
(17, 'Öl (zum Braten)', TRUE, TRUE, TRUE, TRUE);

-- Ingredients für Rösti (Rezept 3)
INSERT INTO ingredient (id, ingredient_name, vegetarisch, vegan, laktose, ingredient_glutenfrei) VALUES
(18, 'Kartoffeln', TRUE, TRUE, TRUE, TRUE),
(19, 'Zwiebeln', TRUE, TRUE, TRUE, TRUE),
(20, 'Butter oder Öl', TRUE, TRUE, TRUE, TRUE),
(21, 'Salz', TRUE, TRUE, TRUE, TRUE),
(22, 'Pfeffer', TRUE, TRUE, TRUE, TRUE);

-- Ingredients für Rüebli Suppe (Rezept 4)
INSERT INTO ingredient (id, ingredient_name, vegetarisch, vegan, laktose, ingredient_glutenfrei) VALUES
(23, 'Karotten (Rüebli)', TRUE, TRUE, TRUE, TRUE),
(24, 'Zwiebeln', TRUE, TRUE, TRUE, TRUE),
(25, 'Knoblauch', TRUE, TRUE, TRUE, TRUE),
(26, 'Butter', TRUE, FALSE, FALSE, TRUE),
(27, 'Gemüsebrühe', TRUE, TRUE, TRUE, TRUE),
(28, 'Sahne', TRUE, FALSE, FALSE, TRUE),
(29, 'Ingwer', TRUE, TRUE, TRUE, TRUE),
(30, 'Salz', TRUE, TRUE, TRUE, TRUE),
(31, 'Pfeffer', TRUE, TRUE, TRUE, TRUE);

-- Ingredients für Milchreis (Rezept 5)
INSERT INTO ingredient (id, ingredient_name, vegetarisch, vegan, laktose, ingredient_glutenfrei) VALUES
(32, 'Rundkornreis', TRUE, TRUE, TRUE, TRUE),
(33, 'Milch', TRUE, FALSE, FALSE, TRUE),
(34, 'Zucker', TRUE, TRUE, TRUE, TRUE),
(35, 'Vanillezucker', TRUE, TRUE, TRUE, TRUE),
(36, 'Zimt', TRUE, TRUE, TRUE, TRUE),
(37, 'Butter', TRUE, FALSE, FALSE, TRUE),
(38, 'Salz', TRUE, TRUE, TRUE, TRUE),
(39, 'Apfelmus', TRUE, TRUE, TRUE, TRUE);

-- =============================================
-- INSERT Statements für die 5 Rezepte
-- =============================================

-- 1. Hörnli-Auflauf
INSERT INTO recipes (recipe_id, recipe_name, recipe_instruction, recipe_mengenangaben, recipes_ingredient) VALUES (
    1,
    'Hörnli-Auflauf',
    '1. Ofen auf 200°C vorheizen.\n2. Hörnli nach Packungsanleitung al dente kochen.\n3. Währenddessen Schinken in kleine Würfel schneiden.\n4. Käse fein reiben.\n5. Eier mit Milch, Salz, Pfeffer und Muskatnuss verquirlen.\n6. Abgetropfte Hörnli mit Schinken und der Hälfte des Käses vermischen.\n7. In eine gefettete Auflaufform geben.\n8. Eiermilch darüber giessen.\n9. Mit restlichem Käse bestreuen.\n10. Im vorgeheizten Ofen 25-30 Minuten backen bis goldbraun und stockt.',
    '4 Portionen',
    1
);

-- 2. Bananen Pancakes
INSERT INTO recipes (recipe_id, recipe_name, recipe_instruction, recipe_mengenangaben, recipes_ingredient) VALUES (
    2,
    'Bananen Pancakes',
    '1. Bananen mit einer Gabel zu einem Mus zerdrücken.\n2. Eier hinzufügen und gut verrühren.\n3. Mehl, Backpulver und Zimt unterrühren.\n4. Milch nach und nach hinzufügen, bis ein glatter, dickflüssiger Teig entsteht.\n5. Etwas Öl in einer beschichteten Pfanne erhitzen.\n6. Pro Pancake 1-2 Esslöffel Teig in die Pfanne geben.\n7. Bei mittlerer Hitze backen, bis sich Blasen auf der Oberfläche bilden.\n8. Wenden und von der anderen Seite goldbraun backen.\n9. Warm mit Ahornsirup servieren.',
    '2 Portionen',
    2
);

-- 3. Rösti
INSERT INTO recipes (recipe_id, recipe_name, recipe_instruction, recipe_mengenangaben, recipes_ingredient) VALUES (
    3,
    'Rösti',
    '1. Kartoffeln schälen und grob reiben.\n2. Die geriebenen Kartoffeln in einem Küchentuch kräftig ausdrücken, um möglichst viel Feuchtigkeit zu entfernen.\n3. Zwiebel fein hacken und mit den Kartoffeln vermischen.\n4. Salz und Pfeffer hinzufügen.\n5. Butter oder Öl in einer Pfanne erhitzen.\n6. Kartoffelmasse in die heisse Pfanne geben und gleichmässig flach drücken.\n7. Bei mittlerer Hitze 10-12 Minuten braten, bis die Unterseite goldbraun ist.\n8. Rösti auf einen Teller stürzen, zurück in die Pfanne gleiten lassen und weitere 10-12 Minuten braten.\n9. Direkt servieren.',
    '3 Portionen',
    3
);

-- 4. Rüebli Suppe
INSERT INTO recipes (recipe_id, recipe_name, recipe_instruction, recipe_mengenangaben, recipes_ingredient) VALUES (
    4,
    'Rüebli Suppe',
    '1. Zwiebel und Knoblauch fein hacken.\n2. Karotten schälen und in Scheiben schneiden.\n3. In einem grossen Topf Butter schmelzen.\n4. Zwiebel und Knoblauch glasig dünsten.\n5. Karotten hinzufügen und 5 Minuten mitdünsten.\n6. Mit Gemüsebrühe ablöschen.\n7. 20-25 Minuten köcheln lassen, bis die Karotten weich sind.\n8. Vom Herd nehmen und mit einem Stabmixer fein pürieren.\n9. Sahne einrühren und mit Salz, Pfeffer und frischem Ingwer abschmecken.\n10. Nochmals kurz erwärmen, nicht mehr kochen lassen.',
    '4 Portionen',
    4
);

-- 5. Milchreis
INSERT INTO recipes (recipe_id, recipe_name, recipe_instruction, recipe_mengenangaben, recipes_ingredient) VALUES (
    5,
    'Milchreis',
    '1. Milch in einem schweren Topf aufkochen.\n2. Rundkornreis und eine Prise Salz unterrühren.\n3. Hitze reduzieren und bei schwacher Hitze 30-35 Minuten köcheln lassen, gelegentlich umrühren.\n4. Wenn der Reis die Milch aufgesogen hat und cremig ist, Zucker und Vanillezucker unterrühren.\n5. Vom Herd nehmen und Butter unterrühren.\n6. Zugedeckt 10 Minuten ziehen lassen.\n7. Vor dem Servieren nochmals auflockern.\n8. Mit Zimt bestreut und Apfelmus servieren.',
    '4 Portionen',
    5
);
 