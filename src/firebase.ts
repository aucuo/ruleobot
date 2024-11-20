import admin from "firebase-admin";

// Импортируем файл конфигурации
import serviceAccount from "./serviceAccountKey.json";

admin.initializeApp({
    credential: admin.credential.cert(serviceAccount as admin.ServiceAccount),
    databaseURL: "https://ruleobot-default-rtdb.europe-west1.firebasedatabase.app"
});

const db = admin.firestore();

export { admin, db };
