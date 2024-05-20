"use strict";
const loginPage = document.getElementById('login');
const feedPage = document.getElementById('feed');
const loginForm = document.getElementById('loginForm');
const firstNameInput = document.getElementById('firstName');
const participantIdInput = document.getElementById('participantId');
const loginButton = document.getElementById('loginButton');
const indicatorLabel = loginButton.querySelector('.indicator-label');
const indicatorProgress = loginButton.querySelector('.indicator-progress');
const logoutBtn = document.getElementById("logoutBtn");
let loadingCurrentPage = false;
const reactionsMap = {
  Like: "L",
  Love: "LV",
  CARE: "C",
  Wow: "W",
  Haha: "H",
  Sad: "S",
  Angry: "A"
}
// Function to disable the button
function disableButton(thisBtn) {
  thisBtn.disabled = true;
}
// Function to enable the button
function enableButton(thisBtn) {
  thisBtn.disabled = false;
}

function checkAndShowReminder() {
  // const modalElement = document.getElementById('survey-reminder-modal');
  // const modal = new bootstrap.Modal(document.getElementById('survey-reminder-modal'));
  const currentTime = new Date().getTime();
  const loginTime = parseInt(sessionStorage.getItem("loginTime"));
  if (!isNaN(loginTime)) {
    const intervalDuration = SURVEY_REMINDER_MINUTES * 60 * 1000;
    if ((currentTime >= loginTime + intervalDuration)) {
      $('#back-to-survey').removeClass('d-none');
    }
  }
}

// Set an interval to run every minute
setInterval(checkAndShowReminder, (1 * 60 * 1000));

document.getElementById('back-to-survey').addEventListener('click', async () => {
  await updateSession(false);
});

// document.getElementById('continue-news-feed').addEventListener('click', async () => {
//   await updateSession(true);
// });

async function updateSession(isActive) {
  await fetch('/api/participants/update_session/', {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      is_active: isActive,
      end_time: new Date().toISOString(),
      session: sessionStorage.getItem("sessionId")
    })
  });
  // try {
  //   const data = await response.json();
  //   if (!response.ok) {
  //     console.error('Failed to update session:', data);
  //   } else {
  //     console.log('Session updated successfully:', data);
  //   }
  // } catch (error) {
  //   console.error('Error in response:', error);
  // }
  if (!isActive) {
    performLogout()
  }
}

const sendData = (endpoint, jsonData, postProcessFunc, method) => {
  jsonData.participant = sessionStorage.getItem("participantUUID");
  jsonData.session = sessionStorage.getItem("sessionId");
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
      // performLogout();
    });
};

function showLoader() {
  loadingCurrentPage = true;
  $('#loading').show();
}
function hideLoader() {
  loadingCurrentPage = false;
  $('#loading').hide();
}
function isValidUUIDv4(uuid) {
  const uuidPattern =
    /^[0-9A-F]{8}-[0-9A-F]{4}-[4][0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$/i;
  return uuidPattern.test(uuid);
}

function handleErrors(errors) {
  // Clear previous error messages

  // Display error messages for each field
  if (errors.participant) {
    showError(participantIdInput, errors.participant);
  }
  if (errors.first_name) {
    showError(firstNameInput, errors.first_name);
  }
  // Handle other error fields as needed

}

function showError(input, message) {
  const formGroup = input.parentElement;
  const errorElement = document.createElement('div');
  errorElement.classList.add('text-danger', 'mt-2');
  errorElement.textContent = message;
  formGroup.appendChild(errorElement);
}

function clearErrors() {
  const errorElements = document.querySelectorAll('.text-danger');
  errorElements.forEach(error => error.remove());
}

const performLogout = () => {
  clearErrors()
  sessionStorage.clear();
  document.querySelector("#articleContainer").innerHTML = "";
  currentPage = "/api/articles";
  loginForm.reset();
  loginPage.classList.remove("d-none");
  feedPage.classList.add("d-none");
}
logoutBtn.addEventListener("click", function (e) {
  e.preventDefault();
  performLogout();
});

let currentPage = "/api/articles?";
if (pageName.includes("high")) {
  currentPage += new URLSearchParams({
    min_pc1: 0.75,
    max_pc1: 1,
  })
} else if (pageName.includes("low")) {
  currentPage += new URLSearchParams({
    min_pc1: 0,
    max_pc1: 0.25,
  })
}
document.body.addEventListener('click', function (event) {
  let target = event.target;
  if (target.classList.contains('read-more-btn') || target.parentElement.classList.contains('read-more-btn')) {
    disableButton(target);
    target = target.classList.contains('read-more-btn') ? target : target.parentElement;
    sendData("/api/read-entire-article-clicks/", { article: target.dataset.id }, () => {
      enableButton(target);

    });
  }
});


(function () {
  /**
   * Easy selector helper function
   */
  const select = (el, all = false) => {
    el = el.trim()
    if (all) {
      return [...document.querySelectorAll(el)]
    } else {
      return document.querySelector(el)
    }
  }

  /**
   * Easy on scroll event listener 
   */
  const onscroll = (el, listener) => {
    el.addEventListener('scroll', listener)
  }

  /**
   * Navbar links active state on scroll
   */
  let navbarlinks = select('#navbar .scrollto', true)
  const navbarlinksActive = () => {
    let position = window.scrollY + 200
    navbarlinks.forEach(navbarlink => {
      if (!navbarlink.hash) return
      let section = select(navbarlink.hash)
      if (!section) return
      if (position >= section.offsetTop && position <= (section.offsetTop + section.offsetHeight)) {
        navbarlink.classList.add('active')
      } else {
        navbarlink.classList.remove('active')
      }
    })
  }
  window.addEventListener('load', navbarlinksActive)
  onscroll(document, navbarlinksActive)

  /**
   * Back to top button
   */
  let backtotop = select('.back-to-top')
  if (backtotop) {
    const toggleBacktotop = () => {
      if (window.scrollY > 100) {
        backtotop.classList.add('active')
      } else {
        backtotop.classList.remove('active')
      }
    }
    window.addEventListener('load', toggleBacktotop)
    onscroll(document, toggleBacktotop)
  }
})()


$('.User-avtar').click(function (e) {
  e.stopPropagation();
  $('.User-Dropdown').toggleClass("U-open");
});

$(document).click(function (e) {
  if (!$(e.target).closest('.dropdown').length) {
    $('.User-Dropdown').removeClass("U-open");
  }
});


loginForm.addEventListener('submit', async (event) => {
  event.preventDefault();

  const firstName = firstNameInput.value.trim();
  const participantId = participantIdInput.value.trim();
  const formData = {
    participant: participantId,
    first_name: firstName,
    login_website_type: pageName
  };

  try {
    indicatorLabel.classList.add('d-none');
    indicatorProgress.classList.remove('d-none');
    const response = await fetch('/api/participants/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData)
    });
    const data = await response.json();
    if (!response.ok) {
      // Handle API error
      handleErrors(data);
    } else {
      // login success
      clearErrors();
      loginPage.classList.add('d-none');
      feedPage.classList.remove('d-none');
      sessionStorage.setItem("sessionId", data.id);
      sessionStorage.setItem("participantUUID", data.participant_id);
      sessionStorage.setItem("participantId", participantId);
      sessionStorage.setItem("firstName", firstName);
      document.getElementById("firstNameContainer").textContent = firstName;
      document.getElementById("participantIdSpan").textContent = participantId;
      feedLoad();

      // Store the current time as login time
      const loginTime = new Date().getTime(); // get current time in milliseconds
      sessionStorage.setItem("loginTime", loginTime);
      sessionStorage.setItem("lastSurveyReminderTime", loginTime);
    }

  } catch (error) {
    console.error('Error:', error);
  } finally {
    indicatorLabel.classList.remove('d-none');
    indicatorProgress.classList.add('d-none');
  }
});

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
          let commentContent = ""
          if (article["comments"]) {
            for (const comment of article["comments"]) {
              commentContent += `
                <!-- Single comment -->
                <div class="d-flex mb-3">
                  <span class="comment user-icon img-wrapper rounded-circle me-4">
                    <i class="fa-solid fa-circle-user"></i>
                  </span>
                  <div class="flex-grow-1">
                    <div class="bg-light rounded-3">
                      <span class="text-dark mb-0">
                        <strong>${sessionStorage.getItem("firstName")}</strong>
                      </span>
                      <span class="text-muted d-block">
                        <small>${comment["content"]}</small>
                      </span>
                    </div>
                  </div>
                </div>
                <!-- Single comment -->
              `
            }
          }
          const articleHTML = `
            <div class="col-sm-8 mx-auto mb-7">
              <div class="card bg-light">
                <!-- Media Content -->
                <div class="card-body p-5 p-sm-8">
                  <div class="d-flex align-items-center mb-4">
                    <a href="${article.url}" target="blank" class="user-icon img-wrapper border rounded-circle me-2 read-more-btn" data-id="${article.id}">
                      <img src="${article.publisher_image}" class="img-fluid" alt="" />
                    </a>
                    <div class="d-flex flex-column lh-sm ">
                      <a href="${article.url}" target="blank" class="text-dark mb-0 fw-bold mb-1 read-more-btn" data-id="${article.id}">
                        ${article.publisher || article.publisher_domain} </a>
                      <span class="text-muted fs-8 " style="margin-top:-2px">
                        ${new Date(article.published_at).toLocaleDateString(
            "en-us",
            {
              weekday: "long",
              year: "numeric",
              month: "short",
              day: "numeric",
            }
          )}
                      </span>
                    </div>
                  </div>
                  <div>
                    <h2 class="fs-4">${article.title}</h2>
                    <p class="m-0">${article.description}</p>
                  </div>
                </div>
                <!-- Media Content -->
                <!-- Media -->
                <div class="media-image position-relative float-btn-outer">
                  <div class="img-wrapper">
                    <img src="${article.image_url}" class="img-fluid">
                  </div>
                  <a href="${article.url}" target="blank" class="float-btn read-more-btn" data-id="${article.id}">
                    <span class="btn btn-dark-primary fs-7">Read More</span>
                  </a>
                </div>
                <!-- Media -->
                <!-- Buttons -->
                <div class="card-body p-5 p-sm-8 py-sm-3 d-flex align-items-center flex-column justify-content-center " style="min-height: 61px;">
                  <div class="d-flex justify-content-between text-center  align-items-center w-100" style="min-height: 37px;">
                    <!--Reaction button-->
                    <div class="col text-start">
                      <button type="button" data-id="${article.id}" class="react-btn btn btn-link btn-link-primary btn-lg text-decoration-none text-muted p-0 d-inline-flex align-items-center position-relative">
                        <span class="icon-container d-inline-flex align-items-center ">
                          <span class="react-icon">
                            <i class="fas fa-thumbs-up fs-4 me-2"></i>
                          </span>
                          <span class="icon-title">Like</span>
                        </span>
                        <div class="emoji-container">
                          <div class="emoji-icon">
                            <div class="emoji like">
                              <div class="icon" data-title="Like"></div>
                            </div>
                          </div>
                          <div class="emoji-icon">
                            <div class="emoji love">
                              <div class="icon" data-title="Love"></div>
                            </div>
                          </div>
                          <div class="emoji-icon">
                            <div class="emoji haha">
                              <div class="icon" data-title="Haha"></div>
                            </div>
                          </div>
                          <div class="emoji-icon">
                            <div class="emoji wow">
                              <div class="icon" data-title="Wow"></div>
                            </div>
                          </div>
                          <div class="emoji-icon">
                            <div class="emoji sad">
                              <div class="icon" data-title="Sad"></div>
                            </div>
                          </div>
                          <div class="emoji-icon">
                            <div class="emoji angry">
                              <div class="icon" data-title="Angry"></div>
                            </div>
                          </div>
                        </div>
                      </button>
                    </div>
                    <!--Reaction button-->
                 <!--read more button-->
                <div class="col">
                  <a
                    class="btn btn-link btn-link-primary btn-lg text-decoration-none text-muted p-0 d-inline-flex align-items-center read-more-btn"
                    href="${article.url}" target="blank" data-id="${article.id}"
                  >
                    <i class="fa-brands fa-readme fs-4 me-2"></i> Read More
                  </a>
                </div>
                <!--read more button-->

                    <!--Share button-->
                    <div class="col text-end">
                      <div class="dropdown">
                        <button type="button" class="btn btn-link btn-link-primary btn-lg text-decoration-none text-muted p-0 d-inline-flex align-items-center" data-bs-toggle="dropdown" aria-expanded="false" data-bs-auto-close="outside">
                          <i class="fa-solid fa-share fs-7 me-2"></i>Share </button>
                        <div class="share-dropdown-menu dropdown-menu text-body-secondary border-0 p-0" style="max-width: max-content;">
                          <div class="wrap text-center p-3">
                            <!-- Begin Share -->
                            <div class="share">
                              <a href="https://www.facebook.com/share.php?u=${article.url}" target="blank" data-id="${article.id}" data-type="FB" class="share-social-btn share-facebook">
                                <i class="fa-brands fa-facebook-f"></i>
                              </a>
                              <a href="https://www.reddit.com/submit?url=${article.url}"  data-id="${article.id}" data-type="R" target="blank" class="share-social-btn share-reddit fs-4">
                                <i class="fa-brands fa-reddit"></i>
                              </a>
                              <a href="https://twitter.com/intent/tweet?url=${article.url}" data-id="${article.id}" data-type="X" target="blank" class="share-social-btn share-twitter fs-4">
                                <i class="fa-brands fa-x-twitter"></i>
                              </a>
                              <a  href="https://www.linkedin.com/sharing/share-offsite/?url=${article.url}" data-id="${article.id}" data-type="L" target="blank" class="share-social-btn share-linkedin">
                                <i class="fa-brands fa-linkedin-in fs-6"></i>
                              </a>
                              <a href="javascript: void(0);" class="more_link" title="Link">
                                <i class="fa-solid fa-link"></i>
                              </a>
                            </div>
                            <!-- End Share -->
                            <!-- Begin Link -->
                            <div class="link">
                              <input class="form-control c-form-control" id="share-embed${article.id}" name="link" type="text" readonly="" value="${article.url}">
                                <button class="share-btn copy-link text-muted text-hover-primary" title="Copy to Clipboard" type="button" data-copytarget="#share-embed${article.id}" data-id=${article.id}>
                                  <i class="fa-solid fa-copy"></i>
                                </button>
                                <button class="share-btn no-link text-muted text-hover-primary" title="Back" type="button">
                                  <i class="fa-solid fa-arrow-up fs-8"></i>
                                </button>
                            </div>
                            <!-- End Link -->
                          </div>
                        </div>
                      </div>
                    </div>
                    <!--Share button-->
                  </div>
                  <!-- Comments -->
                  <div class="mt-3 pt-6 border-top border-gray-300 w-100">
                    <!-- Input -->
                    <div class="d-flex mb-3">
                      <span class="comment user-icon img-wrapper rounded-circle me-4">
                        <i class="fa-solid fa-circle-user"></i>
                      </span>
                      <div class="form-outline w-100">
                        <form class="nav nav-item w-100 position-relative">
                          <input type="hidden" name="article" value="${article.id}">
                          <textarea data-autoresize="" name="content" class="form-control pe-8 bg-light fs-7 " rows="1" placeholder="Write a comment..."></textarea>
                          <button class="text-muted bg-transparent px-3 pe-5 position-absolute top-50 end-0 translate-middle-y border-0 text-hover-primary" type="submit">
                            <i class="fa-solid fa-paper-plane fs-7"></i>
                          </button>
                        </form>
                      </div>
                    </div>
                    <!-- prev comments -->
                    <div class="pt-3" id="commentBox${article.id}">
                    ${commentContent}
                    </div>
                    <!-- prev comments -->
                  </div>
                </div>
                <!-- Buttons -->
              </div>
        </div>
        `
          container.innerHTML += articleHTML;
        });
      })
      .catch((error) => {
        console.error("error from api:", error);
        // performLogout();
      })
      .finally(() => {
        hideLoader();
      });
  }
};

if (
  isValidUUIDv4(sessionStorage.getItem("sessionId")) &&
  isValidUUIDv4(sessionStorage.getItem("participantUUID")) &&
  sessionStorage.getItem("participantId")
) {
  document.getElementById("participantIdSpan").textContent =
    sessionStorage.getItem("participantId");
  document.getElementById("firstNameContainer").textContent =
    sessionStorage.getItem("firstName");

  feedPage.classList.remove("d-none");
  feedLoad();
} else {
  loginPage.classList.remove("d-none");
}

// Link
$(document).on('click', '.more_link', function () {
  $(".share").toggleClass("active");
  $(".link").toggleClass("active");
});

$(document).on('click', '.share-btn.no-link', function () {
  $(".link").removeClass("active");
  $(".share").removeClass("active");
});

$(document).on('click', '.share', function () {
  $(".fa-share").toggleClass("expanded");
});

// Dropdown
$(document).on("click.bs.dropdown", '.dropdown-menu.share-menu', function (e) {
  e.stopPropagation();
  e.preventDefault();
});

document.addEventListener('hide.bs.dropdown', function () {
  $(".link").removeClass("active");
  $(".share").removeClass("active");
  $(".fa-share").removeClass("expanded");
});


$(document).on('click', '.copy-link', function () {
  const copyText = $(this).data('copytarget');
  const inp = copyText ? $(copyText)[0] : null;
  if (inp && inp.select) {
    inp.select();
    inp.setSelectionRange(0, 99999); // For mobile devices
    try {
      navigator.clipboard.writeText(inp.value);
      sendData("/api/share-clicks/", { article: $(this).data('id'), shared_on: "C" }, () => { });
      inp.blur();
      $(this).addClass('copied');
      setTimeout(function () {
        $('.copy-link').removeClass('copied');
      }, 1000);
    } catch (err) {
      alert('Please press Ctrl/Cmd+C to copy');
    }
  }
});

$(document).on('click', '.react-btn', function (event) {

  const emojiContainer = $(this).find('.emoji-container');
  const iconContainer = $(this).find('.icon-container');
  let target = $(event.target).closest('.react-btn')[0];

  if (!iconContainer.hasClass('selected-emoji')) {
    emojiContainer.addClass('active');
    iconContainer.find('.react-icon').html('<div class="emoji like"><div class="icon" data-title="Like"></div></div>');
    iconContainer.addClass('selected-emoji');
    sendData(
      "/api/reactions/",
      { article: target.dataset.id, type: "L" },
      () => { },
    );
  }
  else {
    if (emojiContainer.hasClass('active')) {
      iconContainer.removeClass('selected-emoji')
      iconContainer.find('.react-icon').html('<i class="fas fa-thumbs-up fs-4 me-2"></i>');
      iconContainer.find('.icon-title').text('Like');
      sendData(
        "/api/reactions/delete_reaction/",
        { article: target.dataset.id, type: "L" },
        () => { },
        "DELETE"
      );
    }
    else {
      emojiContainer.addClass('active');
    }
  }
});

$(document).on('click', '.share-social-btn', function (event) {
  const specificShareBtn = event.target.classList.contains('share-social-btn') ? event.target : event.target.parentElement;
  disableButton(specificShareBtn);
  sendData("/api/share-clicks/", { article: specificShareBtn.dataset.id, shared_on: specificShareBtn.dataset.type }, () => {
    enableButton(specificShareBtn);
  });
});

$(document).on('click', '.emoji-container .emoji-icon', function (event) {
  const emojiIcon = $(this).html();
  const emojiTitle = $(this).find('.icon').data('title');
  const iconContainer = $(this).closest('.react-btn').find('.icon-container');
  const target = $(event.target).closest('.react-btn')[0];
  iconContainer.find('.react-icon').html(emojiIcon);
  iconContainer.addClass('selected-emoji');
  iconContainer.find('.icon-title').text(emojiTitle);
  $(this).closest('.emoji-container').removeClass('active');
  sendData(
    "/api/reactions/",
    { article: target.dataset.id, type: reactionsMap[emojiTitle] },
    () => { },
  );
});

const createComment = function (form) {
  const articleId = form.querySelector('input[name="article"]').value;
  const commentText = form.querySelector('textarea').value.trim();
  if (commentText !== "") {
    sendData("/api/comments/", { article: articleId, content: commentText }, (data) => {
      // Clear the textarea after getting the value
      form.querySelector('textarea').value = '';
      const commentContent = `
        <div class="d-flex mb-3">
          <span class="comment user-icon img-wrapper rounded-circle me-4">
            <i class="fa-solid fa-circle-user"></i>
          </span>
          <div class="flex-grow-1">
            <div class="bg-light rounded-3">
              <span class="text-dark mb-0">
                <strong>${sessionStorage.getItem("firstName")}</strong>
              </span>
              <span class="text-muted d-block">
                <small>${data.content}</small>
              </span>
            </div>
          </div>
        </div>
      `;
      // Append the new comment to the appropriate comment box
      document.getElementById(`commentBox${articleId}`).innerHTML += commentContent;
    });

  }
}

document.addEventListener("DOMContentLoaded", function () {
  document.body.addEventListener('keydown', function (event) {
    if (event.target.tagName === 'TEXTAREA' && event.key === 'Enter') {
      event.preventDefault(); // Prevent the default Enter action (new line)
      createComment(event.target.closest('form'))
    }
  });
  document.querySelector("#articleContainer").addEventListener('submit', function (event) {
    event.preventDefault(); // Prevent the default form submission
    createComment(event.target.closest('form'))
  });
});

