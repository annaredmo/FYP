// Submit the comment
async function submitComment() {
  var comment = commentTextarea.value;
  hideCommentModal();

  id = document.getElementById("playlist-id-playlist").value;
  username = document.getElementById("username-playlist").value;

   const data = {
      comment: comment,
      spotifyLink: id,
      username:username
   };
   console.log(data, id);

    const response = await fetch('/update_comments', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({table_data: data})
  });
  if (response.ok) {
    console.log('Table data was successfully sent to the server');
    var tableBody = document.getElementById("commentlist");
    var newRow = document.createElement("tr");
    var newCell = document.createElement("td");
    newCell.textContent = comment+" by "+username; /* TODO doesnt have font */
    newRow.appendChild(newCell);
    tableBody.appendChild(newRow);

  } else {
    console.error('Network response was not ok');
  }
}

  async function incrementLikes() {
    var countEl = document.getElementById('like-count');
    var count = parseInt(countEl.innerHTML);
    countEl.innerHTML = count + 1;

    var spotifyLink = document.getElementById("playlist-id-playlist").value;
    const data = {
      likes: count+1,
      spotifyLink: spotifyLink
    };

    console.log('spotify',data)

    const response = await fetch('/update_likes', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({table_data: data})
  });
  if (response.ok) {
    console.log('Table data was successfully sent to the server');
  } else {
    console.error('Network response was not ok');
  }
  }