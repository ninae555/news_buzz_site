// Initializing
let currentPage = 1;
let isLoading = false;

document.addEventListener('DOMContentLoaded', () => {
  // Initial Load
  loadArticles();
  
  // Infinite Scroll
  window.addEventListener('scroll', () => {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 1000 && !isLoading) {
      loadArticles();
    }
  });

  // Filtering mechanism
//   document.getElementById('filterByPublisher').addEventListener('change', () => {
//     currentPage = 1; // Reset to the first page
//     document.getElementById('articles').innerHTML = ''; // Clear existing articles
//     loadArticles();
//   });
});

// Function to Load Articles
const loadArticles = () => {
  isLoading = true;
  // const publisherFilter = document.getElementById('filterByPublisher').value;
  fetch(`/api/articles?page=${currentPage}`)
    .then(response => response.json())
    .then(data => {
      currentPage++;
      appendArticles(data);
      isLoading = false;
    });
};

// Function to append articles to the DOM
// Function to append articles to the DOM
const appendArticles = (articles) => {
  const articleContainer = document.getElementById('articles');

  articles.forEach(article => {
      const articleDiv = document.createElement('div');
      articleDiv.classList.add('col-12');
      articleDiv.innerHTML = `
          <div class="card mb-4">
              <img src="${article.image_url || '/static/images/placeholder.png'}" class="card-img-top" alt="...">
              <div class="card-body">
                  <h5 class="card-title">${article.title}</h5>
                  <p class="card-text">${article.description}</p>
                  <small class="text-muted">Published by ${article.publisher}</small><br>
                  <small class="text-muted">Date: ${new Date(article.published_at).toLocaleString()}</small>
                  <a href="${article.url}" class="btn btn-primary mt-2">Read More</a>
                  <button class="btn btn-light like-btn">Like</button>
                  <div class="comments-section mt-2">
                      <input type="text" placeholder="Add a comment..."/>
                      <button class="btn btn-secondary submit-comment">Submit</button>
                  </div>
                  <button class="btn btn-info share-btn mt-2">Share</button>
              </div>
          </div>
      `;

      articleContainer.appendChild(articleDiv);

      // Like button listener
      const likeBtn = articleDiv.querySelector('.like-btn');
      likeBtn.addEventListener('click', (e) => {
          console.log("like")
          e.preventDefault();
          fetch('/api/like/', {
              method: 'POST',
              body: JSON.stringify({
                  article: article.id
              }),
              headers: {
                  'Content-Type': 'application/json'
              }
          })
          .then(response => response.json())
          .then(data => {
              if (data.message === "Article liked!") {
                  likeBtn.textContent = "Liked!";
              }
          });
      });

      // Share button listener
      const shareBtn = articleDiv.querySelector('.share-btn');
      shareBtn.addEventListener('click', (e) => {
          console.log("share")
          e.preventDefault();
          fetch('/api/share/', {
              method: 'POST',
              body: JSON.stringify({
                  article_id: article.id
              }),
              headers: {
                  'Content-Type': 'application/json'
              }
          })
          .then(response => response.json())
          .then(data => {
              if (data.message === "Article shared!") {
                  alert('Article shared successfully!');
              }
          });
      });

      // Read More button listener
      const readMoreBtn = articleDiv.querySelector('.btn-primary');
      readMoreBtn.addEventListener('click', (e) => {
          console.log("readmore")
          fetch('/api/click/', {
              method: 'POST',
              body: JSON.stringify({
                  article_id: article.id
              }),
              headers: {
                  'Content-Type': 'application/json'
              }
          });
      });

      // Comment button listener
      const submitCommentBtn = articleDiv.querySelector('.submit-comment');
      const commentInput = articleDiv.querySelector('.comments-section input');
      submitCommentBtn.addEventListener('click', (e) => {
        console.log("comment")
          e.preventDefault();
          const commentText = commentInput.value;
          if (commentText.trim() === '') return;  // Avoid empty comments
          fetch('/api/comment/', {
              method: 'POST',
              body: JSON.stringify({
                  article_id: article.id,
                  comment: commentText
              }),
              headers: {
                  'Content-Type': 'application/json'
              }
          })
          .then(response => response.json())
          .then(data => {
              if (data.message === "Comment added!") {
                  commentInput.value = '';  // Clear the input field after submitting
              }
          });
      });
  });
};




/* Project specific Javascript goes here. */
// Initializing

// document.addEventListener("DOMContentLoaded", () => {
//   // Initial Load
//   loadArticles();

//   // Infinite Scroll
//   window.addEventListener("scroll", () => {
//     if (
//       window.innerHeight + window.scrollY >=
//         document.body.offsetHeight - 1000 &&
//       !isLoading
//     ) {
//       loadArticles();
//     }
//   });

//   // Filtering mechanism
//   document
//     .getElementById("filterByPublisher")
//     .addEventListener("change", () => {
//       currentPage = 1; // Reset to the first page
//       document.getElementById("articles").innerHTML = ""; // Clear existing articles
//       loadArticles();
//     });
// });

// // Function to Load Articles
// const loadArticles = () => {
//   isLoading = true;

//   // Simulate API response with static data
//   const articles = [
//     {
//       title: "Climate Change Impacts",
//       description:
//         "A deep dive into the impacts of climate change on our planet.",
//       url: "#",
//       published_by: "ClimateBuzz",
//       created_at: new Date().toLocaleString(),
//       image: null,
//     },
//     {
//       title: "Carbon Footprint",
//       description: "What is carbon footprint and why it matters?",
//       url: "#",
//       published_by: "EcoNews",
//       created_at: new Date().toLocaleString(),
//       image: null,
//     },
//     // ... more static articles
//   ];

//   // Simulate network delay
//   setTimeout(() => {
//     currentPage++;
//     appendArticles(articles);
//     isLoading = false;
//   }, 500);
// };

// // Function to append articles to the DOM
// const appendArticles = (articles) => {
//   const articleContainer = document.getElementById("articles");
//   articles.forEach((article) => {
//     const articleDiv = document.createElement("div");
//     articleDiv.classList.add("col-md-4");
//     articleDiv.innerHTML = `
//       <div class="card mb-4">
//         <img src="${
//           article.image || "https://www.un.org/sites/un2.un.org/files/thumbnail_image001.png"
//         }" class="card-img-top" alt="...">
//         <div class="card-body">
//           <h5 class="card-title">${article.title}</h5>
//           <p class="card-text">${article.description}</p>
//           <small class="text-muted">Published by ${
//             article.published_by
//           }</small><br>
//           <small class="text-muted">Date: ${article.created_at}</small>
//           <a href="${article.url}" class="btn btn-primary mt-2">Read More</a>
//         </div>
//       </div>
//     `;
//     articleContainer.appendChild(articleDiv);
//   });
// };
