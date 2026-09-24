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
  const [isSignUp, setIsSignUp] = useState(false);
  const [fullName, setFullName] = useState('');
  const [username, setUsername] = useState('');
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
      'Google Account Sign-In / Sign-Up',
      'Select how you would like to proceed with Google:',
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
          text: 'Quick Sign-In (yashsony23478@gmail.com)',
          onPress: () => {
            setEmail('yashsony23478@gmail.com');
            setUsername('yashsony23478');
            setPassword('admin123');
            setIsSignUp(false);
          }
        },
        { text: 'Cancel', style: 'cancel' }
      ]
    );
  };

  const handleEmailAuth = async () => {
    if (isSignUp) {
      // Sign Up Flow
      if (!username.trim() || !password.trim()) {
        Alert.alert('Validation Error', 'Please enter both a username and password');
        return;
      }

      setLoading(true);
      try {
        await axiosClient.post('/auth/register', {
          username: username.trim(),
          email: email.trim() || undefined,
          full_name: fullName.trim() || username.trim(),
          password: password.trim()
        }, {
          headers: { 'Bypass-Tunnel-Reminder': 'true' }
        });

        // Auto login after successful registration
        const encodedData = `username=${encodeURIComponent(username.trim())}&password=${encodeURIComponent(password.trim())}`;
        const response = await axiosClient.post('/auth/login', encodedData, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Bypass-Tunnel-Reminder': 'true'
          },
        });

        const token = response.data.access_token;
        const userResponse = await axiosClient.get('/auth/me', {
          headers: { Authorization: `Bearer ${token}` }
        });

        const { signIn } = useAuthStore.getState();
        await signIn(token, userResponse.data);
        Alert.alert('Success', 'Account registered and signed in successfully!');

      } catch (error: any) {
        Alert.alert('Sign Up Failed', error.response?.data?.detail || 'Could not create account');
      } finally {
        setLoading(false);
      }

    } else {
      // Sign In Flow
      const loginId = username.trim() || email.trim();
      if (!loginId || !password.trim()) {
        Alert.alert('Validation Error', 'Please enter your username/email and password');
        return;
      }

      setLoading(true);
      try {
        const encodedData = `username=${encodeURIComponent(loginId)}&password=${encodeURIComponent(password.trim())}`;
        const response = await axiosClient.post('/auth/login', encodedData, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Bypass-Tunnel-Reminder': 'true'
          },
        });

        const token = response.data.access_token;
        const userResponse = await axiosClient.get('/auth/me', {
          headers: { Authorization: `Bearer ${token}` }
        });

        const { signIn } = useAuthStore.getState();
        await signIn(token, userResponse.data);

      } catch (error: any) {
        if (error.response?.status === 401 || error.response?.status === 400) {
          Alert.alert('Login Failed', error.response?.data?.detail || 'Incorrect username or password');
        } else {
          Alert.alert('Connection Error', 'Could not connect to server. Please check connection.');
        }
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <KeyboardAvoidingView 
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'} 
      style={styles.container}
    >
      <ScrollView contentContainerStyle={styles.scrollContainer} keyboardShouldPersistTaps="handled">
        <View style={styles.card}>
          <Text style={styles.title}>SAIDEEP JEWELLERS</Text>
          <Text style={styles.subtitle}>
            {isSignUp ? 'Create a New Account' : 'Sign in to your account'}
          </Text>

          {/* 1. Primary Top Action: Sign in / Sign up with Google */}
          <TouchableOpacity 
            style={[styles.googleButton, (loading || googleLoading) && styles.buttonDisabled]} 
            onPress={handleGoogleSignInPress}
            disabled={loading || googleLoading}
          >
            {googleLoading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <View style={styles.googleButtonContent}>
                <Ionicons name="logo-google" size={22} color="#EA4335" style={{ marginRight: 10 }} />
                <Text style={styles.googleButtonText}>
                  {isSignUp ? 'Sign Up with Google' : 'Sign In with Google'}
                </Text>
              </View>
            )}
          </TouchableOpacity>

          {/* Divider */}
          <View style={styles.dividerRow}>
            <View style={styles.dividerLine} />
            <Text style={styles.dividerText}>OR WITH EMAIL</Text>
            <View style={styles.dividerLine} />
          </View>

          {/* 2. Email & Password Input Fields */}
          {isSignUp && (
            <View style={styles.inputContainer}>
              <Text style={styles.label}>Full Name</Text>
              <TextInput
                style={styles.input}
                placeholder="Yash Soni"
                placeholderTextColor="#666"
                value={fullName}
                onChangeText={setFullName}
                editable={!loading && !googleLoading}
              />
            </View>
          )}

          <View style={styles.inputContainer}>
            <Text style={styles.label}>Username</Text>
            <TextInput
              style={styles.input}
              placeholder="admin / your username"
              placeholderTextColor="#666"
              value={username}
              onChangeText={setUsername}
              autoCapitalize="none"
              editable={!loading && !googleLoading}
            />
          </View>

          {isSignUp && (
            <View style={styles.inputContainer}>
              <Text style={styles.label}>Email Address</Text>
              <TextInput
                style={styles.input}
                placeholder="you@example.com"
                placeholderTextColor="#666"
                value={email}
                onChangeText={setEmail}
                keyboardType="email-address"
                autoCapitalize="none"
                editable={!loading && !googleLoading}
              />
            </View>
          )}

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
            onPress={handleEmailAuth}
            disabled={loading || googleLoading}
          >
            {loading ? (
              <ActivityIndicator color="#000" />
            ) : (
              <Text style={styles.buttonText}>
                {isSignUp ? 'Create Account' : 'Sign In'}
              </Text>
            )}
          </TouchableOpacity>

          {/* 3. Switch between Sign In and Sign Up */}
          <View style={styles.toggleRow}>
            <Text style={styles.toggleText}>
              {isSignUp ? 'Already have an account? ' : "Don't have an account? "}
            </Text>
            <TouchableOpacity onPress={() => setIsSignUp(!isSignUp)}>
              <Text style={styles.toggleLink}>
                {isSignUp ? 'Sign In' : 'Sign Up with Email'}
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a0a',
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
    fontSize: 24,
    fontWeight: 'bold',
    color: '#d4af37',
    textAlign: 'center',
    marginBottom: 6,
    textTransform: 'uppercase',
    letterSpacing: 1.5,
  },
  subtitle: {
    fontSize: 13,
    color: '#888',
    textAlign: 'center',
    marginBottom: 22,
  },
  googleButton: {
    backgroundColor: '#1f1f1f',
    borderWidth: 1,
    borderColor: '#444',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 3,
  },
  googleButtonContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  googleButtonText: {
    color: '#fff',
    fontSize: 15,
    fontWeight: '700',
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
    marginHorizontal: 10,
    color: '#666',
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 1,
  },
  inputContainer: {
    marginBottom: 14,
  },
  label: {
    fontSize: 11,
    fontWeight: 'bold',
    color: '#888',
    textTransform: 'uppercase',
    marginBottom: 6,
  },
  input: {
    backgroundColor: '#0a0a0a',
    borderWidth: 1,
    borderColor: '#333',
    borderRadius: 8,
    padding: 13,
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
    fontSize: 15,
    fontWeight: 'bold',
  },
  toggleRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 20,
  },
  toggleText: {
    color: '#888',
    fontSize: 13,
  },
  toggleLink: {
    color: '#d4af37',
    fontSize: 13,
    fontWeight: 'bold',
    textDecorationLine: 'underline',
  }
});
