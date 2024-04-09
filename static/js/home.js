document.addEventListener('DOMContentLoaded', () => {
    const firebaseConfig = {
      apiKey: "AIzaSyBF-gktODbomUIyPOT_MWuGqxFwDP-Mx8I",
      authDomain: "placementpredictor.firebaseapp.com",
      databaseURL: "https://placementpredictor-default-rtdb.firebaseio.com",
      projectId: "placementpredictor",
      storageBucket: "placementpredictor.appspot.com",
      messagingSenderId: "712644933317",
      appId: "1:712644933317:web:1ffede201bcd0764c322ac",
      measurementId: "G-WE3JELDMP5"
    };
  
    firebase.initializeApp(firebaseConfig);
    window.firebaseApp = firebase.app();
    window.auth = firebase.auth();
    window.db = firebase.firestore();
  
    const handleLogout = async () => {
      const user = firebase.auth().currentUser;
      if (user) {
        user.getIdToken(true).then(idToken => {
          console.log('Attempting to logout...');
          try {
            fetch('/logout', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + idToken
              }
            }).then(response => {
              console.log('User logged out successfully.');
              window.location.href = '/'; // Redirect to login page after logout
            }).catch(error => {
              console.error('Error signing out: ', error);
            });
          } catch (error) {
            console.error('Error signing out: ', error);
          }
        }).catch(error => {
          console.error('Error getting ID token: ', error);
        });
      }
    };
  
    const logoutButton = document.querySelector('.menu-item-logout');
    if (logoutButton) {
      logoutButton.addEventListener('click', handleLogout);
    }
  });