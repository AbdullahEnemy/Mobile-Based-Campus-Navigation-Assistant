import React, { useState } from "react";
import {
  StyleSheet,
  Text,
  View,
  Image,
  TouchableOpacity,
  StatusBar,
  ActivityIndicator,
  ScrollView,
} from "react-native";
import * as ImagePicker from "expo-image-picker";
import * as FileSystem from "expo-file-system";
import axios from "axios";

export default function App() {
  const [image, setImage] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  const uploadImage = async (uri) => {
    try {
      setLoading(true);
      const fileInfo = await FileSystem.getInfoAsync(uri);
      const fileUri = fileInfo.uri;

      const formData = new FormData();
      formData.append("image", {
        uri: fileUri,
        name: "image.jpg",
        type: "image/jpeg",
      });

      const response = await axios.post(
        "http://192.168.100.9:5000/predict",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      if (response.data) {
        setPrediction(response.data);
      } else {
        setPrediction({ error: "No response data" });
      }
    } catch (err) {
      console.error(err);
      setPrediction({ error: "Something went wrong" });
    } finally {
      setLoading(false);
    }
  };

  const openCamera = async () => {
    const permissionResult = await ImagePicker.requestCameraPermissionsAsync();
    if (!permissionResult.granted) {
      alert("Camera permission is required!");
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      allowsEditing: true,
      quality: 1,
    });

    if (!result.canceled) {
      const uri = result.assets[0].uri;
      setImage(uri);
      await uploadImage(uri);
    }
  };

  const openGallery = async () => {
    const permissionResult =
      await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permissionResult.granted) {
      alert("Gallery access is required!");
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      allowsEditing: true,
      quality: 1,
    });

    if (!result.canceled) {
      const uri = result.assets[0].uri;
      setImage(uri);
      await uploadImage(uri);
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#121212" />
      <Text style={styles.title}>📷 Campus Navigator</Text>

      <TouchableOpacity style={styles.button} onPress={openCamera}>
        <Text style={styles.buttonText}>Capture Image</Text>
      </TouchableOpacity>

      <TouchableOpacity
        style={[styles.button, { backgroundColor: "#4CAF50" }]}
        onPress={openGallery}
      >
        <Text style={styles.buttonText}>Select From Gallery</Text>
      </TouchableOpacity>

      {image && (
        <View style={styles.imageContainer}>
          <Image source={{ uri: image }} style={styles.image} />
        </View>
      )}

      {loading && (
        <ActivityIndicator
          size="large"
          color="#00bcd4"
          style={{ marginTop: 20 }}
        />
      )}

      {prediction && !prediction.error && (
        <View style={styles.resultBox}>
          <Text style={styles.resultText}>
            🏢 Landmark: {prediction.landmark}
          </Text>
          <Text style={styles.resultText}>
            📏 Distance: {prediction.estimated_distance} meters
          </Text>
        </View>
      )}

      {prediction && prediction.error && (
        <Text style={{ color: "red", marginTop: 20 }}>{prediction.error}</Text>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingTop: 60,
    paddingBottom: 40,
    backgroundColor: "#1e1e1e",
    alignItems: "center",
    justifyContent: "flex-start",
    paddingHorizontal: 20,
    minHeight: "100%",
  },
  title: {
    fontSize: 28,
    color: "#fff",
    marginBottom: 40,
    fontWeight: "bold",
  },
  button: {
    backgroundColor: "#00bcd4",
    paddingVertical: 14,
    paddingHorizontal: 24,
    borderRadius: 12,
    elevation: 3,
    marginVertical: 10,
    width: "80%",
    alignItems: "center",
  },
  buttonText: {
    color: "#fff",
    fontSize: 18,
    fontWeight: "600",
  },
  imageContainer: {
    marginTop: 30,
    borderRadius: 12,
    overflow: "hidden",
    borderWidth: 2,
    borderColor: "#00bcd4",
  },
  image: {
    width: 300,
    height: 300,
    resizeMode: "cover",
  },
  resultBox: {
    marginTop: 30,
    backgroundColor: "#333",
    padding: 20,
    borderRadius: 10,
  },
  resultText: {
    fontSize: 18,
    color: "#fff",
    marginVertical: 5,
  },
});
