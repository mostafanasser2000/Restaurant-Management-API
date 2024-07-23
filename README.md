# Restaurant-Management-API

This my implementation to the final project of [API'S](https://www.coursera.org/learn/apis) course from [Meta Back-End Developer Professional Certificate](https://www.coursera.org/professional-certificates/meta-back-end-developer#courses) Using [Django REST FrameWork](https://www.django-rest-framework.org/)

## Youtube Video Preview
[![API Preview](https://img.youtube.com/vi/Om1G0e3M0sI/0.jpg)](https://www.youtube.com/watch?v=Om1G0e3M0sI)



## Main Features

- **User Management**

  - Register users, generate authentication tokens, and enforce role-based access control for user types like managers, delivery crew, and customers..

- **Menu Items:**

  - Perform CRUD operations on menu items, with fine-grained access control based on user roles.

- **User Groups:**

  - Manage user groups for managers and delivery crew, allowing seamless assignment and removal of users from specific roles.

- **Cart Management:**

  - Enable users to add and remove menu items from their carts, providing a streamlined shopping experience.

- **Order Management:**

  - Create, update, and view orders with associated order items. Managers and delivery crew can update order statuses.

## Installation

- Create folder for project

```shell
mkdir <name-for-project>
cd <name-for-project>
```

- Inside created folder create virtual environment

```shell
python3 -m venv <virtual enviroment name>
```

- clone project to this folder

```shell
git clone https://github.com/mostafanasser2000/RestaurantAPI.git
```

- activate eniviroment

```shell
source <virtual enviroment name>/bin/activate
```

- Install requirements

```shell
pip3 install -r requirements.txt
```

- Open project folder with any IDE
- run this migrate commands

```shell
python3 manage.py migrate
```

- run tests

```shell
python3 manage.py test
```

- create super user (Admin)

```shell
python3 manage.py createsuperuser
```

- run development server

```shell
python3 manage.py runserver
```

- navigate to documentation page to see endpoints

```shell
http://127.0.0.1:8000/api/v1/schema/swagger-ui/
```

## End Points

### User registration and token generation endpoints

| Endpoint                      | Role                                   | Method   | Purpose                                                                     |
| ----------------------------- | -------------------------------------- | -------- | --------------------------------------------------------------------------- |
| **/accounts/users/**          | No role required                       | **POST** | Creates a new user with username, email and password                        |
| **/accounts/users/users/me/** | Anyone with a valid user token         | **GET**  | Displays only the current user                                              |
| **/auth/token/login/**        | Anyone with a valid email and password | **POST** | Generates access tokens that can be used in other API calls in this project |

### Menu-items endpoints

| Endpoint                          | Role           | Method         | Purpose                                                      |
| --------------------------------- | -------------- | -------------- | ------------------------------------------------------------ |
| **/api/v1/menu-items/**           | Any One        | **GET**        | Lists all menu items. Return a **200 – Ok** HTTP status code |
| **/api/menu-items**               | Admin, Manager | **POST**       | Creates a new menu item and returns 201 - Created            |
| **/api/menu-items/{menuItemID}/** | Admin, Manager | **PUT, PATCH** | Updates single menu item                                     |
| **/api/menu-items/{menuItemID}/** | Admin, Manager | **DELETE**     | Deletes menu item                                            |

### User groups management endpoints

| Endpoint                            | Role           | Method     | Purpose                                                                                                                                                        |
| ----------------------------------- | -------------- | ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | 
| **/api/v1/managers/**               | Admin          | **GET**    | Returns all managers                                                                                                                                           |
| **/api/v1/managers/**               | Admin          | **POST**   | Assigns the user in the payload to the manager group and returns **201-Created**                                                                               |
| **/api/v1/managers/{userId}/**      | Admin          | **DELETE** | Removes this particular user from the manager group and returns **200 – Success** if everything is okay. If the user is not found, returns **404 – Not found** |
| **/api/v1/delivery-crew/**          | Admin, Manager | **GET**    | Returns all delivery crew                                                                                                                                      |
| **/api/v1/delivery-crew/**          | Admin, Manager | **POST**   | Assigns the user in the payload to delivery crew group and returns **201-Created HTTP**                                                                        |
| **/api/v1/delivery-crew/{userId}/** | Admin,Manager  | **DELETE** | Removes this user from the manager group and returns **200 – Success** if everything is okay.If the user is not found, returns **404 – Not found**             |

### Cart management endpoints

| Endpoint                       | Role     | Method     | Purpose                                                |
| ------------------------------ | -------- | ---------- | ------------------------------------------------------ |
| **/api/v1/cart/**              | Customer | **GET**    | Returns current items in the cart for the current user |
| **/api/cart/menu-items/**      | Customer | **POST**   | Adds a menu item to the cart.                          |
| **/api/v1/cart/{menuitemId}/** | Customer | **DELETE** | Remove menu item from cart                             |

### Order management endpoints

| Endpoint                     | Role           | Method         | Purpose                                                                                                                                                                                           |
| ---------------------------- | -------------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **/api/v1/orders/**          | Customer       | **GET**        | Returns all orders with order items created by this user                                                                                                                                          |
| **/api/v1/orders/**          | Customer       | **POST**       | Creates a new order item for the current user. Gets current cart items from the cart endpoints and adds those items to the order items table. Then deletes all items from the cart for this user. |
| **/api/v1/orders/{orderId}** | Customer       | **GET**        | Returns all items for this order id. If the order ID doesn’t belong to the current user, Returns. returns **403 – Unauthorized**                                                                  |
| **/api/v1/orders**           | Admin, Manager | **GET**        | Return all orders                                                                                                                                                                                 |
| **/api/orders/{orderId}**    | Admin, Manager | **PUT, PATCH** | Updates the order. A manager can use this endpoint to set a delivery crew to this order, and also update the order status                                                                         |
| **/api/orders/{orderId}**    | Admin, Manager | **DELETE**     | Deletes this order                                                                                                                                                                                |
| **/api/orders/{orderId}**    | Delivery crew  | **PATCH**      | A delivery crew can use this endpoint to update the order status                                                                                                                                  |
