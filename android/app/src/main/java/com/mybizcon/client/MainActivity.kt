package com.mybizcon.client

import android.app.Activity
import android.os.Bundle
import android.provider.Settings
import android.content.Intent
import android.net.Uri
import android.view.Gravity
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView

/**
 * Minimal launcher activity for myBIZcon Android thin client.
 *
 * The app's main work is done by AccessibilityService and overlay service;
 * this activity gives users a stable entry point and permission shortcuts.
 */
class MainActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            setPadding(48, 48, 48, 48)
        }

        val title = TextView(this).apply {
            text = getString(R.string.app_name)
            textSize = 24f
            gravity = Gravity.CENTER
        }

        val description = TextView(this).apply {
            text = getString(R.string.main_activity_description)
            textSize = 15f
            gravity = Gravity.CENTER
            setPadding(0, 24, 0, 32)
        }

        val accessibilityButton = Button(this).apply {
            text = getString(R.string.open_accessibility_settings)
            setOnClickListener {
                startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS))
            }
        }

        val overlayButton = Button(this).apply {
            text = getString(R.string.open_overlay_settings)
            setOnClickListener {
                val intent = Intent(
                    Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                    Uri.parse("package:$packageName")
                )
                startActivity(intent)
            }
        }

        layout.addView(title)
        layout.addView(description)
        layout.addView(accessibilityButton)
        layout.addView(overlayButton)
        setContentView(layout)
    }
}
