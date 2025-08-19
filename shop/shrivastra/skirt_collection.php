<?php
include('db.php');
$result = mysqli_query($conn, "SELECT * FROM skirt_collection");
?>
<!DOCTYPE html>
<html>
<head>
  <title>Skirt Collection</title>
  <style>
    body {
      font-family: 'Poppins', sans-serif;
      background: #fff0f5;
      margin: 0;
      padding: 0;
    }

    h1 {
      text-align: center;
      padding: 20px;
      color: #c2185b;
    }

    /* 💖 Outer Box */
    .collection-box {
      background: #ffffff;
      max-width: 1100px;
      margin: 30px auto;
      padding: 25px;
      border-radius: 20px;
      box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
      gap: 20px;
    }

    .card {
      background: #fff;
      padding: 15px;
      border-radius: 16px;
      box-shadow: 0 6px 12px rgba(0,0,0,0.08);
      text-align: center;
      transition: transform 0.2s;
    }

    .card:hover {
      transform: translateY(-5px);
    }

    .card img {
      width: 100%;
      height: 240px;
      object-fit: cover;
      border-radius: 12px;
      margin-bottom: 10px;
    }

    .card h2 {
      color: #880e4f;
      margin: 10px 0 5px;
    }

    .card p {
      font-size: 14px;
      color: #555;
    }

    .price {
      color: #d81b60;
      font-weight: bold;
      margin: 10px 0;
    }

    .qty-controls {
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 12px;
      margin-top: 10px;
    }

    .qty-controls button {
      background: #d63384;
      color: white;
      border: none;
      padding: 6px 12px;
      font-size: 16px;
      border-radius: 50%;
      cursor: pointer;
      transition: background 0.2s;
    }

    .qty-controls button:hover {
      background: #ad1457;
    }

    .qty-controls span {
      font-size: 18px;
      font-weight: bold;
      color: #333;
    }
  </style>
</head>
<body>

<h1>🧁 Skirt Collection - Shrivasra</h1>

<!-- 💖 Wrap entire collection in a beautiful box -->
<div class="collection-box">
  <div class="grid">
    <?php while ($row = mysqli_fetch_assoc($result)) { ?>
      <div class="card">
        <img src="<?php echo $row['image']; ?>" alt="Skirt Image">
        <h2><?php echo $row['title']; ?></h2>
        <p><?php echo $row['description']; ?></p>
        <p class="price">₹<?php echo $row['price']; ?></p>
        <div class="qty-controls">
          <button onclick="updateCart(<?php echo $row['id']; ?>, -1)">−</button>
          <span id="qty-<?php echo $row['id']; ?>">0</span>
          <button onclick="updateCart(<?php echo $row['id']; ?>, 1)">+</button>
        </div>
      </div>
    <?php } ?>

  </div>
</div>

<script>
  let cart = {};
  function updateCart(id, change) {
    if (!cart[id]) cart[id] = 0;
    cart[id] += change;
    if (cart[id] < 0) cart[id] = 0;
    document.getElementById("qty-" + id).innerText = cart[id];
  }
</script>

</body>
</html>
