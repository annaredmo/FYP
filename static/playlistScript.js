/*
 *   playlistScript.js - Javascript functions for the playlist screen
 */

// call server to add a new comment in databse for playlist
// and comment to screen
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

  try {
    const response = await fetch('/update_comments', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({table_data: data})
    });

    if (response.ok) {
      console.log('Added comment')
      var tableBody = document.getElementById("commentlist");
      var newRow = document.createElement("tr");
      var newCell = document.createElement("td");
      newCell.textContent = comment+" by "+username;
      newRow.appendChild(newCell);
      tableBody.appendChild(newRow);
    } else {
      console.error('Network response was not ok');
    }
  } catch (error) {
    console.error('There was an error:', error);
  }
}

// call server to update likes in databse for playlist
// and update likes on screen
async function incrementLikes() {

  var countEl = document.getElementById('like-count');
  var count = parseInt(countEl.innerHTML);

  var spotifyLink = document.getElementById("playlist-id-playlist").value;
  const data = {
    likes: count+1,
    spotifyLink: spotifyLink
  };

  try {
    const response = await fetch('/update_likes', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({table_data: data})
    });

    if (!response.ok) {
      console.error('Network response was not ok');
    } else {
      console.log('Added like')
      countEl.innerHTML = count + 1;
    }
  } catch (error) {
    console.error('IncrementLikes:', error);
  }
}
