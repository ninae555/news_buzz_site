let currentPage = "/api/articles?";
if (pageName == "feed_high_pc1") {
  currentPage += new URLSearchParams({
    min_pc1: 0.75,
    max_pc1: 1,
  })
} else if (pageName == "feed_low_pc1") {
  currentPage += new URLSearchParams({
    min_pc1: 0,
    max_pc1: 0.25,
  })
}
let loadingCurrentPage = false;
const loginForm = document.getElementById("loginForm");
const logoutBtn = document.getElementById("logoutBtn");
const submitButton = loginForm.querySelector('button[type="submit"]');
const loginPage = document.getElementById("loginPage");
const feedPage = document.getElementById("feedPage");
const dropdownToggle = document.querySelector("#dropdownUser");
const dropdownMenu = document.querySelector(".origin-top-right");
const participantError = document.getElementById("participantError");
// const first_nameError = document.getElementById("first_nameError");
function disableButton(thisBtn) {
  thisBtn.disabled = true;
  thisBtn.classList.add("opacity-50", "cursor-not-allowed");
}
// Function to enable the button
function enableButton(thisBtn) {
  thisBtn.disabled = false;
  thisBtn.classList.remove("opacity-50", "cursor-not-allowed");
}
// Function to get text color based on reaction type
function getTextColor(reactionType, isCurrentReaction) {
  const colorMappings = {
    L: "blue-600",
    LV: "red-600",
    C: "yellow-600",
    W: "purple-600",
    H: "green-600",
    S: "blue-400",
    A: "red-400",
  };

  return isCurrentReaction
    ? `text-${colorMappings[reactionType]}`
    : `hover:text-${colorMappings[reactionType]}`;
}

function unsecuredCopyToClipboard(text) {
  const textArea = document.createElement("textarea");

  // Style the textarea to be invisible and out of the viewport
  textArea.style.position = 'fixed'; // Prevents scrolling to the bottom
  textArea.style.opacity = '0'; // Makes it invisible
  textArea.style.left = '-9999px'; // Positions it out of the viewport
  textArea.style.top = '0'; // Keeps it at the top to avoid any potential scroll

  textArea.value = text;
  document.body.appendChild(textArea);
  textArea.focus();
  textArea.select();

  try {
    document.execCommand('copy');
  } catch (err) {
    console.error('Unable to copy to clipboard', err);
  }

  document.body.removeChild(textArea);
}

const performLogout = () => {
  sessionStorage.clear();
  document.querySelector("#articleContainer").innerHTML = "";
  currentPage = "/api/articles";
  loginForm.reset();
  submitButton.disabled = false;
  submitButton.innerHTML = '<i class="fas fa-sign-in-alt"></i> Login';
  loginPage.classList.remove("hidden");
  feedPage.classList.add("hidden");
  dropdownMenu.style.display = "none";
};
const sendData = (endpoint, jsonData, postProcessFunc, method) => {
  jsonData.participant = sessionStorage.getItem("participantUUID");
  jsonData.session = sessionStorage.getItem("sessionId");
  // console.log("jsonData");
  // console.log(jsonData);
  fetch(endpoint, {
    method: method || "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(jsonData),
  })
    .then((response) => {
      if (!response.ok) {
        // Handle error responses here (e.g., log the error or throw an error)
        throw new Error(`Request failed with status ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      if (postProcessFunc) {
        postProcessFunc(data);
      }
    })
    .catch((error) => {
      console.error("error from api:", error);
      performLogout();
    });
};
const onReadEntireClick = (btn) => {
  disableButton(btn);
  sendData("/api/read-entire-article-clicks/", { article: btn.dataset.id }, () => {
    enableButton(btn);
    window.open(btn.dataset.url, "_blank");
  });
};

const onReactionClick = (btn) => {
  // Fetch the previous reaction from the button's data attribute
  const previousReaction = btn.dataset.articlereaction;

  // The new reaction you clicked
  const newReaction = btn.dataset.type;

  // Disable the button while processing
  disableButton(btn);

  // Determine whether to DELETE or POST based on whether the reaction is already set
  const apiEndpoint =
    previousReaction === newReaction
      ? "/api/reactions/delete_reaction/"
      : "/api/reactions/";
  const method = previousReaction === newReaction ? "DELETE" : "POST";

  sendData(
    apiEndpoint,
    { article: btn.dataset.rid, type: newReaction },
    (data) => {
      enableButton(btn);

      // Update the reaction status in the button's data attribute
      if (method === "DELETE") {
        btn.dataset.articlereaction = "";
      } else {
        btn.dataset.articlereaction = newReaction;
      }

      // Update all buttons to reflect the new reaction
      const buttons = document.querySelectorAll(
        `[data-rid="${btn.dataset.rid}"]`
      );
      buttons.forEach((otherBtn) => {
        const reactionType = otherBtn.dataset.type;
        otherBtn.className = `group text-gray-400 ${getTextColor(
          reactionType,
          btn.dataset.articlereaction === reactionType
        )} text-lg`;
      });
    },
    method
  );
};

const loadArticles = () => {
  if (!loadingCurrentPage) {
    showLoader();
    const container = document.querySelector("#articleContainer");
    fetch(currentPage, {
      headers: {
        session: sessionStorage.getItem("sessionId"),
      },
    })
      .then((response) => {
        if (!response.ok) {
          // Handle error responses here (e.g., log the error or throw an error)
          throw new Error(`Request failed with status ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        currentPage = data.next;
        data.results.forEach((article) => {
          const articleHTML = `
            <div class="rounded-sm overflow-hidden bg-white shadow-sm mt-10">
            <div class="">
            <img src="${article.image_url
            }" alt="image could not be loaded" class="w-full h-96 object-cover">
            </div>
            <div class="p-4 pb-5">
            <h2 class="block text-2xl font-semibold text-gray-700 font-roboto">
                ${article.title}
            </h2>
            <div class="mt-2 flex space-x-4">
                <div class="flex text-gray-400 text-sm items-center">
                    <span class="mr-2 text-xs">
                        Published by:
                    </span>
                    ${article.publisher}
                </div>
                <div class="flex text-gray-400 text-sm items-center">
                    <span class="mr-2 text-xs">
                        <i class="far fa-clock" aria-hidden="true"></i>
                    </span>
                    ${new Date(article.published_at).toLocaleDateString(
              "en-us",
              {
                weekday: "long",
                year: "numeric",
                month: "short",
                day: "numeric",
              }
            )}
                </div>
            </div>
            <p class="text-gray-600 text-md mt-5">
                ${article.description}
            </p>
            
            <!-- Reaction Bar -->
            <div class="flex justify-between items-center mt-4">
                <div class="flex space-x-2">
                <button onclick="onReactionClick(this)" data-articlereaction="${article.reaction
            }" data-type="L" data-rid="${article.id}" 
                class="group text-gray-400 ${article.reaction === "L"
              ? "text-blue-600"
              : "hover:text-blue-600"
            } text-lg">
            <i class="fas fa-thumbs-up fa-lg"></i><span>Like</span>
        </button>
        <button onclick="onReactionClick(this)" data-articlereaction="${article.reaction
            }" data-type="LV" data-rid="${article.id}" 
                class="group text-gray-400 ${article.reaction === "LV"
              ? "text-red-600"
              : "hover:text-red-600"
            }">
            <i class="fas fa-heart fa-lg"></i><span>Love</span>
        </button>
        <button onclick="onReactionClick(this)" data-articlereaction="${article.reaction
            }" data-type="C" data-rid="${article.id}" 
                class="group text-gray-400 ${article.reaction === "C"
              ? "text-yellow-600"
              : "hover:text-yellow-600"
            }">
            <i class="fas fa-face-grin-hearts fa-lg"></i><span>Care</span>
        </button>
        <button onclick="onReactionClick(this)" data-articlereaction="${article.reaction
            }" data-type="W" data-rid="${article.id}" 
                class="group text-gray-400 ${article.reaction === "W"
              ? "text-purple-600"
              : "hover:text-purple-600"
            }">
            <i class="fas fa-surprise fa-lg"></i><span>Wow</span>
        </button>
        <button onclick="onReactionClick(this)" data-articlereaction="${article.reaction
            }" data-type="H" data-rid="${article.id}" 
                class="group text-gray-400 ${article.reaction === "H"
              ? "text-green-600"
              : "hover:text-green-600"
            }">
            <i class="fas fa-laugh fa-lg"></i><span>Haha</span>
        </button>
        <button onclick="onReactionClick(this)" data-articlereaction="${article.reaction
            }" data-type="S" data-rid="${article.id}" 
                class="group text-gray-400 ${article.reaction === "S"
              ? "text-blue-400"
              : "hover:text-blue-400"
            }">
            <i class="fas fa-sad-tear fa-lg"></i><span>Sad</span>
        </button>
        <button onclick="onReactionClick(this)" data-articlereaction="${article.reaction
            }" data-type="A" data-rid="${article.id}" 
                class="group text-gray-400 ${article.reaction === "A"
              ? "text-red-400"
              : "hover:text-red-400"
            }">
            <i class="fas fa-angry fa-lg"></i><span>Angry</span>
        </button>
        
                </div>
                <div>
                    <button data-popup="sharePopup${article.id}" class="share-btn group text-gray-400 hover:text-blue-600"><i
                            class="fas fa-share-nodes fa-lg"></i><span class="group-hover:inline">
                            Share</span></button>
                    <!-- Share Popup -->
                    <div id="sharePopup${article.id}"
                        class="popup-btn hidden absolute w-40 rounded shadow-lg bg-white p-4 flex flex-col items-center">
                        <a href="https://www.facebook.com/share.php?u=${article.url}" target="blank" data-id="${article.id}" data-type="FB" class="fb-share specific-share-btn group text-center mb-2 text-gray-400 hover:text-blue-600"><i
                                class="fab fa-lg fa-facebook"></i><span class="group-hover:inline">
                                Facebook</span></a>
                        <a href="https://www.linkedin.com/sharing/share-offsite/?url=${article.url}" data-id="${article.id}" data-type="L" target="blank" class="linkedin-share specific-share-btn group text-center mb-2 text-gray-400 hover:text-blue-700"><i
                                class="fab fa-lg fa-linkedin"></i><span class="group-hover:inline">
                                LinkedIn</span></a>
                      <a href="https://twitter.com/intent/tweet?url=${article.url}" data-id="${article.id}" data-type="X" target="blank" class="twitter-share specific-share-btn group text-center mb-2 text-gray-400 hover:text-gray-800"><i
                              class="fab fa-lg fa-square-x-twitter"></i><span class="group-hover:inline">
                              Twitter</span></a>
                      <a href="https://www.reddit.com/submit?url=${article.url}"  data-id="${article.id}" data-type="R" target="blank" class="reddit-share specific-share-btn group text-center mb-2 text-gray-400"><i
                                                  class="fab fa-lg fa-reddit"></i><span class="group-hover:inline">
                                                  Reddit</span></a>

                        <button data-link="${article.url}" data-id="${article.id}" data-type="C" class="copy-link group text-center text-gray-400 hover:text-gray-600"><i
                          class="fas fa-lg fa-copy"></i><span class="group-hover:inline"> Copy
                                Link</span></button>
                    </div>
            
                </div>
            </div>
            
            <!-- Comment Section -->
            <!-- <div class="mt-5">
                <input type="text" placeholder="Add a comment" class="p-2 w-full rounded border">
                <div class="mt-3">
                    <h4 class="text-lg font-semibold">Comments:</h4>
                    <p class="text-sm mt-2">User1: Great article!</p>
                    <p class="text-sm mt-2">User2: Thanks for sharing this.</p>
                </div>
            </div> -->
            
            <!-- Read More Button -->
            <button class="mt-4 bg-blue-500 text-white rounded p-2 read-entire-article-btn" data-url="${article.url
            }" data-id=${article.id
            } onclick="onReadEntireClick(this)">Read Entire Article</button>
            </div>
            </div>
            `;
          container.innerHTML += articleHTML;
        });
      })
      .catch((error) => {
        console.error("error from api:", error);
        performLogout();
      })
      .finally(() => {
        hideLoader();
      });
  }
};
function showLoader() {
  loadingCurrentPage = true;
  const loader = document.getElementById("loader");
  loader.classList.remove("hidden");
}
function hideLoader() {
  loadingCurrentPage = false;
  const loader = document.getElementById("loader");
  loader.classList.add("hidden");
}
function feedLoad() {
  loadArticles();
  window.addEventListener("scroll", function () {
    if (
      window.innerHeight + window.scrollY >= document.body.offsetHeight - 500 &&
      currentPage
    ) {
      loadArticles();
    }
  });
}
function isValidUUIDv4(uuid) {
  const uuidPattern =
    /^[0-9A-F]{8}-[0-9A-F]{4}-[4][0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$/i;
  return uuidPattern.test(uuid);
}
document.addEventListener("DOMContentLoaded", function () {
  if (
    isValidUUIDv4(sessionStorage.getItem("sessionId")) &&
    isValidUUIDv4(sessionStorage.getItem("participantUUID")) &&
    sessionStorage.getItem("participantId")
  ) {
    document.getElementById("participantIdSpan").textContent =
      sessionStorage.getItem("participantId");
    feedPage.classList.remove("hidden");
    feedLoad();
  } else {
    loginPage.classList.remove("hidden");
  }
  dropdownMenu.style.display = "none";
  dropdownToggle.addEventListener("click", function () {
    if (dropdownMenu.style.display === "none") {
      dropdownMenu.style.display = "block";
    } else {
      dropdownMenu.style.display = "none";
    }
  });
  logoutBtn.addEventListener("click", function (e) {
    e.preventDefault();
    performLogout();
  });
  window.addEventListener("resize", function () {
    if (window.innerWidth > 640) {
      dropdownMenu.style.display = "none";
    }
  });

  document.addEventListener("click", function (e) {
    const shareBtn = e.target.closest(".share-btn");

    if (shareBtn) {
      const popupId = shareBtn.dataset.popup
      const sharePopup = document.getElementById(popupId);
      sharePopup.classList.toggle("hidden");
      // Find all share buttons
      const allShareButtons = document.querySelectorAll('.share-btn');
      // Loop through all share buttons
      allShareButtons.forEach(btn => {
        const popupId = btn.dataset.popup;
        const sharePopup = document.getElementById(popupId);
        if (btn !== shareBtn) {
          sharePopup.classList.add("hidden");
        }
      });
    }
    const copyLinkBtn = e.target.closest(".copy-link");
    if (copyLinkBtn) {
      disableButton(copyLinkBtn);
      sendData("/api/share-clicks/", { article: copyLinkBtn.dataset.id, shared_on: copyLinkBtn.dataset.type }, () => {
        enableButton(copyLinkBtn);
      });
      unsecuredCopyToClipboard(copyLinkBtn.dataset.link)
      copyLinkBtn.textContent = "Link Copied!";
      setTimeout(() => {
        copyLinkBtn.textContent = "";
        copyLinkBtn.innerHTML =
          '<i class="fas fa-copy"></i><span class=" group-hover:inline"> Copy Link</span>';
      }, 5000);
    }
    const specificShareBtn = e.target.closest(".specific-share-btn");
    if (specificShareBtn) {
      disableButton(specificShareBtn);
      sendData("/api/share-clicks/", { article: specificShareBtn.dataset.id, shared_on: specificShareBtn.dataset.type }, () => {
        enableButton(specificShareBtn);
      });
    }

  });

  loginForm.addEventListener("submit", async function (e) {
    e.preventDefault();
    submitButton.disabled = true;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading';
    // Clear previous errors
    participantError.textContent = "";
    participantError.classList.add("hidden");
    // first_nameError.textContent = "";
    // first_nameError.classList.add("hidden");
    const participant = document.getElementById("participant").value;
    // const first_name = document.getElementById("first_name").value;

    // Check if fields are empty and show error message
    jsValidationErrors = false;
    if (!participant) {
      participantError.textContent = "Participant is required";
      participantError.classList.remove("hidden");
      submitButton.disabled = false;
      jsValidationErrors = true;
      submitButton.innerHTML = '<i class="fas fa-sign-in-alt"></i> Login';
    }
    // if (!first_name) {
    //   first_nameError.textContent = "First Name is required";
    //   first_nameError.classList.remove("hidden");
    //   submitButton.disabled = false;
    //   jsValidationErrors = true;
    //   submitButton.innerHTML = '<i class="fas fa-sign-in-alt"></i> Login';
    // }
    if (jsValidationErrors) {
      return;
    }
    try {
      // const getResponse = await fetch(`/api/participants/${participant}/`);
      // const getData = await getResponse.json();
      // if (!getResponse.ok) {
      //   submitButton.disabled = false;
      //   submitButton.innerHTML = '<i class="fas fa-sign-in-alt"></i> Login';
      //   participantError.textContent = "Invalid credentials";
      //   participantError.classList.remove("hidden");
      //   return;
      // }
      // const participantId = getData.id;
      const postResponse = await fetch("/api/participants/login/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ login_website_type: pageName, participant }), // first_name, 
      });
      const postData = await postResponse.json();
      if (!postResponse.ok) {
        submitButton.disabled = false;
        submitButton.innerHTML = '<i class="fas fa-sign-in-alt"></i> Login';
        participantError.textContent = "Invalid credentials";
        participantError.classList.remove("hidden");
        return;
      }
      sessionStorage.setItem("sessionId", postData.id);
      sessionStorage.setItem("participantUUID", postData.participant_id);
      sessionStorage.setItem("participantId", participant);
      document.getElementById("participantIdSpan").textContent = participant;
    } catch (error) {
      submitButton.disabled = false;
      submitButton.innerHTML = '<i class="fas fa-sign-in-alt"></i> Login';
      participantError.textContent =
        "An error occurred. Please try again later.";
      participantError.classList.remove("hidden");
      return;
    }
    submitButton.disabled = false;
    submitButton.innerHTML = '<i class="fas fa-sign-in-alt"></i> Login';
    loginPage.classList.add("hidden");
    feedPage.classList.remove("hidden");
    feedLoad();
  });
});
