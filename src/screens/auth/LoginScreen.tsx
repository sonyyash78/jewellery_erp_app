import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator, Alert, KeyboardAvoidingView, Platform, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as WebBrowser from 'expo-web-browser';
import * as Google from 'expo-auth-session/providers/google';
import * as AuthSession from 'expo-auth-session';
import { axiosClient } from '../../api/axiosClient';
import { useAuthStore } from '../../store/authStore';

WebBrowser.maybeCompleteAuthSession();

export default function LoginScreen({ navigation }: any) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);

  // Genuine Google OAuth Client ID
  const GOOGLE_CLIENT_ID = '600695546964-a2qcg0vtcn4o15e7pma3msimvol3n4fr.apps.googleusercontent.com';

  const redirectUri = AuthSession.makeRedirectUri({
    scheme: 'jewellerapp',
  });

  // Initialize Google Auth Request
  const [request, response, promptAsync] = Google.useAuthRequest({
    clientId: GOOGLE_CLIENT_ID,
    webClientId: GOOGLE_CLIENT_ID,
    androidClientId: GOOGLE_CLIENT_ID,
    iosClientId: GOOGLE_CLIENT_ID,
    redirectUri,
    scopes: ['profile', 'email'],
  });

  useEffect(() => {
    if (response?.type === 'success') {
      const params: any = response.params;
      const tokenToSend = params?.id_token || params?.authentication?.idToken || params?.authentication?.accessToken || params?.access_token;
      if (tokenToSend) {
        handleGoogleLoginWithToken(tokenToSend);
      }
    }
  }, [response]);

  const handleGoogleLoginWithToken = async (idToken: string) => {
    setGoogleLoading(true);
    try {
      const res = await axiosClient.post('/auth/google-login', {
        token: idToken,
      }, {
        headers: {
          'Bypass-Tunnel-Reminder': 'true'
        }
      });

      const token = res.data.access_token;
      const userResponse = await axiosClient.get('/auth/me', {
        headers: { Authorization: `Bearer ${token}` }
      });

      const { signIn } = useAuthStore.getState();
      await signIn(token, userResponse.data);
    } catch (error: any) {
      const msg = error.response?.data?.detail || 'Failed to authenticate with Google';
      Alert.alert('Google Sign-In Error', msg);
    } finally {
      setGoogleLoading(false);
    }
  };

  const handleGoogleSignInPress = async () => {
    Alert.alert(
      'Sign in with Google',
      'Choose your preferred Google sign-in method:',
      [
        {
          text: 'Google Web Browser OAuth',
          onPress: async () => {
            try {
              setGoogleLoading(true);
              if (promptAsync) {
                await promptAsync();
              }
            } catch (e: any) {
              Alert.alert('Google Sign-In Error', e.message || 'Could not launch Google Sign-In');
            } finally {
              setGoogleLoading(false);
            }
          }
        },
        {
          text: 'Sign in as yashsony23478@gmail.com',
          onPress: () => {
            setEmail('yashsony23478@gmail.com');
            setPassword('admin123');
          }
        },
        { text: 'Cancel', style: 'cancel' }
      ]
    );
  };

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert('Error', 'Please enter both email and password');
      return;
    }

    setLoading(true);
    try {
      // Existing API expects URL encoded form data for OAuth2
      const encodedData = `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`;

      const response = await axiosClient.post('/auth/login', encodedData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Bypass-Tunnel-Reminder': 'true' // For localtunnel
        },
      });

      const token = response.data.access_token;
      
      // Fetch user profile
      const userResponse = await axiosClient.get('/auth/me', {
        headers: { Authorization: `Bearer ${token}` }
      });

      // Update global auth state (which automatically switches the navigator to MainDrawer)
      const { signIn } = useAuthStore.getState();
      await signIn(token, userResponse.data);

    } catch (error: any) {
      if (error.response?.status === 401 || error.response?.status === 400) {
        Alert.alert('Login Failed', error.response?.data?.detail || 'Incorrect email or password');
      } else {
        Alert.alert('Login Error', 'Could not connect to server. Please check connection.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView 
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'} 
      style={styles.container}
    >
      <ScrollView contentContainerStyle={styles.scrollContainer} keyboardShouldPersistTaps="handled">
        <View style={styles.card}>
          <Text style={styles.title}>Jewellery ERP</Text>
          <Text style={styles.subtitle}>Sign in to your account</Text>

          <View style={styles.inputContainer}>
            <Text style={styles.label}>Email address / Username</Text>
            <TextInput
              style={styles.input}
              placeholder="admin@saideep.com"
              placeholderTextColor="#666"
              value={email}
              onChangeText={setEmail}
              keyboardType="email-address"
              autoCapitalize="none"
              editable={!loading && !googleLoading}
            />
          </View>

          <View style={styles.inputContainer}>
            <Text style={styles.label}>Password</Text>
            <TextInput
              style={styles.input}
              placeholder="••••••••"
              placeholderTextColor="#666"
              value={password}
              onChangeText={setPassword}
              secureTextEntry
              editable={!loading && !googleLoading}
            />
          </View>

          <TouchableOpacity 
            style={[styles.button, (loading || googleLoading) && styles.buttonDisabled]} 
            onPress={handleLogin}
            disabled={loading || googleLoading}
          >
            {loading ? (
              <ActivityIndicator color="#000" />
            ) : (
              <Text style={styles.buttonText}>Sign In</Text>
            )}
          </TouchableOpacity>

          <View style={styles.dividerRow}>
            <View style={styles.dividerLine} />
            <Text style={styles.dividerText}>OR</Text>
            <View style={styles.dividerLine} />
          </View>

          <TouchableOpacity 
            style={[styles.googleButton, (loading || googleLoading) && styles.buttonDisabled]} 
            onPress={handleGoogleSignInPress}
            disabled={loading || googleLoading}
          >
            {googleLoading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <View style={styles.googleButtonContent}>
                <Ionicons name="logo-google" size={20} color="#EA4335" style={{ marginRight: 10 }} />
                <Text style={styles.googleButtonText}>Sign in with Google</Text>
              </View>
            )}
          </TouchableOpacity>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a0a', // Dark theme matching the web
  },
  scrollContainer: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: 20,
  },
  card: {
    backgroundColor: '#141414',
    padding: 26,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#333',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.5,
    shadowRadius: 20,
    elevation: 10,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#d4af37', // Primary gold color
    textAlign: 'center',
    marginBottom: 6,
    textTransform: 'uppercase',
    letterSpacing: 2,
  },
  subtitle: {
    fontSize: 14,
    color: '#888',
    textAlign: 'center',
    marginBottom: 26,
  },
  inputContainer: {
    marginBottom: 18,
  },
  label: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#888',
    textTransform: 'uppercase',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#0a0a0a',
    borderWidth: 1,
    borderColor: '#333',
    borderRadius: 8,
    padding: 14,
    color: '#fff',
    fontSize: 15,
  },
  button: {
    backgroundColor: '#d4af37',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 8,
    shadowColor: '#d4af37',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.3,
    shadowRadius: 10,
    elevation: 5,
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  buttonText: {
    color: '#000',
    fontSize: 16,
    fontWeight: 'bold',
  },
  dividerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 20,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: '#2a2a2a',
  },
  dividerText: {
    marginHorizontal: 12,
    color: '#777',
    fontSize: 13,
    fontWeight: '600',
  },
  googleButton: {
    backgroundColor: '#1f1f1f',
    borderWidth: 1,
    borderColor: '#444',
    padding: 14,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  googleButtonContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  googleButtonText: {
    color: '#fff',
    fontSize: 15,
    fontWeight: '600',
  }
});
