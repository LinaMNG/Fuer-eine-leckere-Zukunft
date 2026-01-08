CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(250) NOT NULL UNIQUE,
    password VARCHAR(250) NOT NULL
);


CREATE TABLE todos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    content VARCHAR(100),
    due DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

 CREATE TABLE ingredient (
   id INT AUTO_INCREMENT PRIMARY KEY,
   vegetarisch BOOLEAN,
   vegan BOOLEAN,
   laktose BOOLEAN,
   ingredient_glutenfrei BOOLEAN
);

CREATE TABLE recipes (
  recipe_id INT AUTO_INCREMENT PRIMARY KEY,
  recipe_name VARCHAR(100),
  recipe_photo VARCHAR(200),
  recipe_instruction VARCHAR(4000),
  recipe_mengenangaben VARCHAR(15),
  recipes_ingredient INT(15)
  );
  