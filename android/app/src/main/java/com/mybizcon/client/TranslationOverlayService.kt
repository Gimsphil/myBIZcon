package com.mybizcon.client

import android.app.Service
import android.content.Context
import android.content.Intent
import android.graphics.PixelFormat
import android.os.IBinder
import android.view.Gravity
import android.view.LayoutInflater
import android.view.View
import android.view.WindowManager
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import org.json.JSONObject

/**
 * 📱 TranslationOverlayService
 * Renders an elegant overlay float window on top of WhatsApp (and other messagers).
 * Features:
 * 1. 3 display options: "Translation Only", "Original + Translation", and "Original Only".
 * 2. Elegant suggestion cards to select drafts.
 * 3. Safe injection into the message text box when a draft card is clicked.
 */
class TranslationOverlayService : Service() {

    private lateinit var windowManager: WindowManager
    private var overlayView: View? = null

    // Mode toggles
    private var currentMode = DISPLAY_MODE_DUAL // Default: Original + Translation

    companion object {
        private const val DISPLAY_MODE_TRANSLATION_ONLY = 1
        private const val DISPLAY_MODE_DUAL = 2
        private const val DISPLAY_MODE_ORIGINAL_ONLY = 3
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        windowManager = getSystemService(Context.WINDOW_SERVICE) as WindowManager
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (intent != null && intent.action == "ACTION_UPDATE_TRANSLATION") {
            val rawData = intent.getStringExtra("data") ?: ""
            if (rawData.isNotEmpty()) {
                showOrUpdateOverlay(rawData)
            }
        }
        return START_NOT_STICKY
    }

    /**
     * Dynamically displays the floating overlay with active translation and suggestions.
     */
    private fun showOrUpdateOverlay(jsonData: String) {
        try {
            val rootObj = JSONObject(jsonData)
            val translationText = rootObj.optString("translation", "No translation available.")
            val suggestionsArr = rootObj.optJSONArray("suggestions")

            // Remove existing overlay if present
            removeFloatingOverlay()

            // Set layout params for premium overlay view
            val params = WindowManager.LayoutParams(
                WindowManager.LayoutParams.MATCH_PARENT,
                WindowManager.LayoutParams.WRAP_CONTENT,
                WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN,
                PixelFormat.TRANSLUCENT
            ).apply {
                gravity = Gravity.TOP or Gravity.START
                x = 0
                y = 150 // Draw just below the chat app action bar
            }

            // Inflate mock layout or programmatic view (for pure SDK correctness)
            val layout = LinearLayout(this).apply {
                orientation = LinearLayout.VERTICAL
                setBackgroundColor(0xE6212529.toInt()) // Glassmorphism Dark Theme: Charcoal dark with 90% opacity
                setPadding(30, 20, 30, 20)
            }

            // Translation content text views based on selected Mode
            val translationLabel = TextView(this).apply {
                textSize = 15f
                setTextColor(0xFF00D1B2.toInt()) // Vibrant Teal Cyan
                setPadding(0, 0, 0, 10)
            }

            // Switch Display Modes configuration
            when (currentMode) {
                DISPLAY_MODE_TRANSLATION_ONLY -> {
                    translationLabel.text = "🎯 번역본: $translationText"
                }
                DISPLAY_MODE_DUAL -> {
                    translationLabel.text = "🌐 번역본: $translationText\n⚠️ 원문 기반 분석 완료"
                }
                DISPLAY_MODE_ORIGINAL_ONLY -> {
                    translationLabel.text = "🔍 번역 가능 (탭하여 읽기)"
                }
            }
            layout.addView(translationLabel)

            // Horizontal layout for suggestion drafts buttons (Human in the Loop)
            val suggestionsTitle = TextView(this).apply {
                text = "💡 추천 답변 선택 (HITL)"
                textSize = 12f
                setTextColor(0xFFB5B5B5.toInt())
                setPadding(0, 10, 0, 10)
            }
            layout.addView(suggestionsTitle)

            if (suggestionsArr != null) {
                for (i in 0 until suggestionsArr.length()) {
                    val suggestion = suggestionsArr.getJSONObject(i)
                    val tone = suggestion.optString("tone", "General")
                    val content = suggestion.optString("content", "")

                    val suggestionBtn = Button(this).apply {
                        text = "[$tone] $content"
                        textSize = 13f
                        setTextColor(0xFFFFFFFF.toInt())
                        setBackgroundColor(0xFF2E7D32.toInt()) // Deep Emerald Green for action cards
                        setPadding(20, 10, 20, 10)
                        setOnClickListener {
                            // Inject reply text through the active AccessibilityService instance.
                            MyBIZconAccessibilityService.injectIntoActiveMessenger(content)
                            removeFloatingOverlay()
                        }
                    }
                    layout.addView(suggestionBtn)
                }
            }

            // Add overlay to window manager
            overlayView = layout
            windowManager.addView(overlayView, params)

        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private fun removeFloatingOverlay() {
        overlayView?.let {
            windowManager.removeView(it)
            overlayView = null
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        removeFloatingOverlay()
    }
}
