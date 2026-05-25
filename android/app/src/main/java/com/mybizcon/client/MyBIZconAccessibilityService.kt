package com.mybizcon.client

import android.accessibilityservice.AccessibilityService
import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import org.json.JSONObject
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL
import kotlin.concurrent.thread

/**
 * 🌐 MyBIZconAccessibilityService
 * Core Android Accessibility Service that acts as a thin client for myBIZcon.
 * Implements:
 * 1. Screen Scraping of active WhatsApp chats.
 * 2. Multi-Party Group conversation parsing (mapping individual senders).
 * 3. Rest API synchronization with the FastAPI backend.
 * 4. Human-In-The-Loop Draft text injection directly into input fields.
 */
class MyBIZconAccessibilityService : AccessibilityService() {

    companion object {
        private const val TAG = "myBIZcon_AccessService"
        private const val BACKEND_URL = "http://10.0.2.2:8000/api/v1/chat/message" // Localhost via Android Emulator
        
        // Node Resource IDs for unmodified WhatsApp layouts (crucial for targeted scraping)
        private const val WHATSAPP_MESSAGE_TEXT_ID = "com.whatsapp:id/message_text"
        private const val WHATSAPP_CONVERSATION_TITLE_ID = "com.whatsapp:id/conversation_contact_name"
        private const val WHATSAPP_GROUP_SENDER_NAME_ID = "com.whatsapp:id/sender_name"
        private const val WHATSAPP_INPUT_TEXT_ID = "com.whatsapp:id/entry"
    }

    private var lastScrapedText = ""
    private var activeConversationTitle = ""

    override fun onServiceConnected() {
        super.onServiceConnected()
        Log.i(TAG, "🟢 myBIZcon Accessibility Service connected successfully.")
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent) {
        val rootNode = rootInActiveWindow ?: return
        
        // 1. Detect Conversation Title (Individual or Group name)
        detectConversationTitle(rootNode)

        // 2. Perform Message Scraping and Thread Parsing
        when (event.eventType) {
            AccessibilityEvent.TYPE_WINDOW_CONTENT_CHANGED,
            AccessibilityEvent.TYPE_VIEW_TEXT_CHANGED -> {
                scrapeActiveChatWindow(rootNode)
            }
        }
    }

    /**
     * Identifies the current contact name or group chat name from the top header layout.
     */
    private fun detectConversationTitle(rootNode: AccessibilityNodeInfo) {
        val titleNodes = rootNode.findAccessibilityNodeInfosByViewId(WHATSAPP_CONVERSATION_TITLE_ID)
        if (titleNodes != null && titleNodes.isNotEmpty()) {
            val titleText = titleNodes[0].text?.toString() ?: ""
            if (titleText != activeConversationTitle && titleText.isNotEmpty()) {
                activeConversationTitle = titleText
                Log.d(TAG, "📂 Active Conversation Changed: $activeConversationTitle")
            }
        }
    }

    /**
     * Scrapes all message text nodes inside the active chat window, matching senders
     * for group chats, and routes them to the FastAPI backend.
     */
    private fun scrapeActiveChatWindow(rootNode: AccessibilityNodeInfo) {
        // Find all message bubbles
        val messageNodes = rootNode.findAccessibilityNodeInfosByViewId(WHATSAPP_MESSAGE_TEXT_ID) ?: return
        if (messageNodes.isEmpty()) return

        // Get the latest message bubble node
        val latestMessageNode = messageNodes[messageNodes.size - 1]
        val messageText = latestMessageNode.text?.toString() ?: ""
        
        if (messageText == lastScrapedText || messageText.isEmpty()) return
        lastScrapedText = messageText
        
        // 2.1.2 Multi-Party Group Conversation Support
        // Find if this specific message bubble contains a sender name label (only present in group chats)
        var senderName = "Unknown"
        val parent = latestMessageNode.parent
        if (parent != null) {
            val senderNodes = parent.findAccessibilityNodeInfosByViewId(WHATSAPP_GROUP_SENDER_NAME_ID)
            if (senderNodes != null && senderNodes.isNotEmpty()) {
                senderName = senderNodes[0].text?.toString() ?: "Group Member"
            } else {
                senderName = activeConversationTitle // Direct 1:1 message
            }
        }

        Log.i(TAG, "✉️ Scraped Incoming Msg: [$senderName]: $messageText")

        // Sync with backend API asynchronously
        sendPayloadToBackend(senderName, messageText, activeConversationTitle)
    }

    /**
     * Packages the scraped message context and sends it to the Python backend server.
     */
    private fun sendPayloadToBackend(sender: String, content: String, conversationTitle: String) {
        thread {
            try {
                val url = URL(BACKEND_URL)
                val conn = url.openConnection() as HttpURLConnection
                conn.requestMethod = "POST"
                conn.setRequestProperty("Content-Type", "application/json")
                conn.doOutput = true

                val payload = JSONObject().apply {
                    put("sender", sender)
                    put("content", content)
                    put("conversation_title", conversationTitle)
                    put("timestamp", System.currentTimeMillis())
                }

                val writer = OutputStreamWriter(conn.outputStream)
                writer.write(payload.toString())
                writer.flush()
                writer.close()

                val responseCode = conn.responseCode
                if (responseCode == HttpURLConnection.HTTP_OK) {
                    val responseText = conn.inputStream.bufferedReader().use { it.readText() }
                    Log.d(TAG, "🚀 Sync success: Response: $responseText")
                    
                    // Parse recommendations and launch Overlay display
                    handleBackendRecommendations(responseText)
                } else {
                    Log.e(TAG, "❌ Sync failed: HTTP $responseCode")
                }
                conn.disconnect()
            } catch (e: Exception) {
                Log.e(TAG, "❌ Network connection error: ${e.message}")
            }
        }
    }

    /**
     * Receives response suggestions from the backend and triggers the Floating overlay UI.
     */
    private fun handleBackendRecommendations(jsonResponse: String) {
        // Convert to Broadcast Intent to trigger the TranslationOverlayService
        val intent = Intent(this, TranslationOverlayService::class.java).apply {
            action = "ACTION_UPDATE_TRANSLATION"
            putExtra("data", jsonResponse)
        }
        startService(intent)
    }

    /**
     * 2.3 Real-Time Suggested Reply Generator: Human-in-the-Loop text injection.
     * Receives the user's selected draft from the overlay UI and injects it into WhatsApp's input box.
     */
    fun injectSuggestedReply(draftText: String) {
        val rootNode = rootInActiveWindow ?: return
        val inputNodes = rootNode.findAccessibilityNodeInfosByViewId(WHATSAPP_INPUT_TEXT_ID)
        
        if (inputNodes != null && inputNodes.isNotEmpty()) {
            val inputNode = inputNodes[0]
            val arguments = Bundle().apply {
                putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, draftText)
            }
            // Perform accessibility input injection
            inputNode.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, arguments)
            Log.i(TAG, "✍️ Injected Draft Suggestion to Input Box: $draftText")
        } else {
            Log.e(TAG, "❌ Could not locate WhatsApp input entry box.")
        }
    }

    override fun onInterrupt() {
        Log.w(TAG, "⚠️ Accessibility service interrupted.")
    }
}
