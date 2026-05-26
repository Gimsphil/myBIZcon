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
        private const val NOTES_CAPTURE_URL = "http://10.0.2.2:8000/api/v1/notes/capture"
        private const val WHATSAPP_PACKAGE = "com.whatsapp"
        private const val WHATSAPP_BUSINESS_PACKAGE = "com.whatsapp.w4b"
        private var activeInstance: MyBIZconAccessibilityService? = null

        fun injectIntoActiveMessenger(draftText: String): Boolean {
            // Routes overlay-selected reply text to the running accessibility service.
            return activeInstance?.injectSuggestedReply(draftText) == true
        }

        fun captureNoteFromActiveMessenger(): Boolean {
            return activeInstance?.captureCurrentConversationAsNote() == true
        }
        
        private fun isWhatsAppPackage(packageName: CharSequence?): Boolean {
            val packageText = packageName?.toString()
            return packageText == WHATSAPP_PACKAGE || packageText == WHATSAPP_BUSINESS_PACKAGE
        }
    }

    private var lastScrapedText = ""
    private var activeConversationTitle = ""
    private var lastScrapedSender = "Unknown"
    private var activeWhatsAppPackage = ""

    override fun onServiceConnected() {
        super.onServiceConnected()
        activeInstance = this
        Log.i(TAG, "🟢 myBIZcon Accessibility Service connected successfully.")
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent) {
        val eventPackage = event.packageName
        if (!isWhatsAppPackage(eventPackage)) {
            activeWhatsAppPackage = ""
            return
        }
        activeWhatsAppPackage = eventPackage.toString()
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
        val titleNodes = rootNode.findAccessibilityNodeInfosByViewId(whatsAppViewId("conversation_contact_name"))
        if (titleNodes != null && titleNodes.isNotEmpty()) {
            val titleText = titleNodes[0].text?.toString() ?: ""
            if (titleText != activeConversationTitle && titleText.isNotEmpty()) {
                activeConversationTitle = titleText
                resetScrapedMessageCache()
                Log.d(TAG, "📂 Active Conversation Changed: $activeConversationTitle")
            }
        }
    }

    private fun resetScrapedMessageCache() {
        lastScrapedText = ""
        lastScrapedSender = "Unknown"
    }

    /**
     * Scrapes all message text nodes inside the active chat window, matching senders
     * for group chats, and routes them to the FastAPI backend.
     */
    private fun scrapeActiveChatWindow(rootNode: AccessibilityNodeInfo) {
        // Find all message bubbles
        val messageNodes = rootNode.findAccessibilityNodeInfosByViewId(whatsAppViewId("message_text")) ?: return
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
            val senderNodes = parent.findAccessibilityNodeInfosByViewId(whatsAppViewId("sender_name"))
            if (senderNodes != null && senderNodes.isNotEmpty()) {
                senderName = senderNodes[0].text?.toString() ?: "Group Member"
            } else {
                senderName = activeConversationTitle // Direct 1:1 message
            }
        }

        Log.i(TAG, "✉️ Scraped Incoming Msg: [$senderName]: $messageText")

        lastScrapedSender = senderName

        // Sync with backend API asynchronously
        sendPayloadToBackend(senderName, messageText, activeConversationTitle)
    }

    private fun captureCurrentConversationAsNote(): Boolean {
        if (activeWhatsAppPackage.isBlank()) {
            Log.w(TAG, "Note capture skipped because no active WhatsApp package is selected.")
            return false
        }
        if (lastScrapedText.isBlank()) {
            Log.w(TAG, "Note capture skipped because no active message has been scraped yet.")
            return false
        }
        sendNoteCaptureToBackend(
            title = activeConversationTitle.ifBlank { "Android conversation note" },
            transcript = "${lastScrapedSender}: ${lastScrapedText}"
        )
        return true
    }

    /**
     * Sends the current messenger context to the local HiNoter-style note endpoint.
     */
    private fun sendNoteCaptureToBackend(title: String, transcript: String) {
        thread {
            var conn: HttpURLConnection? = null
            try {
                val url = URL(NOTES_CAPTURE_URL)
                conn = url.openConnection() as HttpURLConnection
                conn.requestMethod = "POST"
                conn.setRequestProperty("Content-Type", "application/json")
                conn.connectTimeout = 10000
                conn.readTimeout = 10000
                conn.doOutput = true

                val payload = JSONObject().apply {
                    put("title", title)
                    put("source_type", "android_overlay")
                    put("source_uri", activeConversationTitle)
                    put("transcript", transcript)
                    put("speaker_labels", org.json.JSONArray().put(lastScrapedSender))
                    put("ask", "Summarize key actions from this conversation.")
                }

                OutputStreamWriter(conn.outputStream).use { writer ->
                    writer.write(payload.toString())
                    writer.flush()
                }

                val responseCode = conn.responseCode
                if (responseCode == HttpURLConnection.HTTP_OK) {
                    val responseText = conn.inputStream.bufferedReader().use { it.readText() }
                    Log.d(TAG, "Note capture success: $responseText")
                } else {
                    Log.e(TAG, "Note capture failed: HTTP $responseCode")
                }
            } catch (e: Exception) {
                Log.e(TAG, "Note capture network error: ${e.message}")
            } finally {
                conn?.disconnect()
            }
        }
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
    fun injectSuggestedReply(draftText: String): Boolean {
        if (activeWhatsAppPackage.isBlank()) {
            Log.w(TAG, "Reply injection skipped because no active WhatsApp package is selected.")
            return false
        }
        val rootNode = rootInActiveWindow ?: return false
        val inputNodes = rootNode.findAccessibilityNodeInfosByViewId(whatsAppViewId("entry"))
        
        if (inputNodes != null && inputNodes.isNotEmpty()) {
            val inputNode = inputNodes[0]
            val arguments = Bundle().apply {
                putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, draftText)
            }
            // Perform accessibility input injection
            val injected = inputNode.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, arguments)
            Log.i(TAG, "✍️ Injected Draft Suggestion to Input Box: $draftText")
            return injected
        } else {
            Log.e(TAG, "❌ Could not locate WhatsApp input entry box.")
            return false
        }
    }

    override fun onInterrupt() {
        Log.w(TAG, "⚠️ Accessibility service interrupted.")
    }

    override fun onDestroy() {
        if (activeInstance === this) {
            activeInstance = null
        }
        super.onDestroy()
    }

    private fun whatsAppViewId(resourceName: String): String {
        return "$activeWhatsAppPackage:id/$resourceName"
    }
}
