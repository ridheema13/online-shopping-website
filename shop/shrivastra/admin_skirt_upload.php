<?php
include('db.php');

// Handle Add Product
if (isset($_POST['add'])) {
    $title = $_POST['title'];
    $desc = $_POST['description'];
    $price = $_POST['price'];
    $image = $_POST['image_url'];

    $sql = "INSERT INTO skirt_collection (image, title, description, price) VALUES ('$image', '$title', '$desc', '$price')";
    mysqli_query($conn, $sql);
    $msg = "Product Added Successfully!";
}

// Handle Delete Product
if (isset($_POST['delete'])) {
    $id = $_POST['delete_id'];
    mysqli_query($conn, "DELETE FROM skirt_collection WHERE id = $id");
    $msg = "Product Deleted Successfully!";
}

$result = mysqli_query($conn, "SELECT * FROM skirt_collection");
?>

<!DOCTYPE html>
<html>
<head>
    <title>Admin - Skirt Upload</title>
    <style>
        body {
            font-family: 'Poppins', sans-serif;
            background: #fff0f6;
            margin: 0;
            padding: 0;
        }

        h1 {
            text-align: center;
            color: #d63384;
            padding: 20px 0;
        }

        .container {
            width: 90%;
            max-width: 1000px;
            margin: auto;
        }

        form {
            background: #fff;
            padding: 20px;
            border-radius: 20px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }

        form input, form textarea {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border-radius: 12px;
            border: 1px solid #ccc;
        }

        form input[type="submit"] {
            background: #d63384;
            color: white;
            border: none;
            cursor: pointer;
            transition: 0.3s;
        }

        form input[type="submit"]:hover {
            background: #b82b70;
        }

        .products {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
        }

        .product-card {
            background: white;
            border-radius: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            padding: 10px;
            text-align: center;
        }

        .product-card img {
            width: 100%;
            height: 180px;
            object-fit: cover;
            border-radius: 12px;
        }

        .delete-btn {
            background: #ff4d4f;
            color: white;
            padding: 6px 12px;
            border: none;
            border-radius: 10px;
            margin-top: 10px;
            cursor: pointer;
        }

        .message {
            text-align: center;
            color: green;
            font-weight: bold;
        }
    </style>
</head>
<body>

<h1>Admin Panel - Skirt Collection</h1>

<div class="container">
    <?php if (isset($msg)) echo "<p class='message'>$msg</p>"; ?>

    <form method="post">
        <h2>Add Product</h2>
        <input type="text" name="title" placeholder="Product Title" required>
        <textarea name="description" placeholder="Description" required></textarea>
        <input type="number" step="0.01" name="price" placeholder="Price ₹" required>
        <input type="url" name="image_url" placeholder="Image URL (https://...)" required>
        <input type="submit" name="add" value="Add Product">
    </form>

    <div class="products">
        <?php while ($row = mysqli_fetch_assoc($result)) { ?>
            <div class="product-card">
                <img src="<?php echo $row['image']; ?>" alt="Skirt Image">
                <h3><?php echo $row['title']; ?></h3>
                <p><?php echo $row['description']; ?></p>
                <p><strong>₹<?php echo $row['price']; ?></strong></p>
                <form method="post">
                    <input type="hidden" name="delete_id" value="<?php echo $row['id']; ?>">
                    <input type="submit" name="delete" value="Delete" class="delete-btn">
                </form>
            </div>
        <?php } ?>
    </div>
</div>
</body>
</html>
