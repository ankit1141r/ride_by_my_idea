// Top-level build file where you can add configuration options common to all sub-projects/modules.
plugins {
    id("com.android.application") version "8.3.2" apply false
    id("com.android.library") version "8.3.2" apply false
    id("org.jetbrains.kotlin.android") version "1.9.20" apply false
    id("com.google.devtools.ksp") version "1.9.20-1.0.14" apply false
    id("com.google.dagger.hilt.android") version "2.48" apply false
    id("com.google.gms.google-services") version "4.4.0" apply false
    id("io.gitlab.arturbosch.detekt") version "1.23.4"
    id("jacoco")
}

buildscript {
    dependencies {
        classpath("com.google.android.libraries.mapsplatform.secrets-gradle-plugin:secrets-gradle-plugin:2.0.1")
    }
}

tasks.register("clean", Delete::class) {
    delete(rootProject.buildDir)
}

// Detekt configuration
detekt {
    buildUponDefaultConfig = true
    allRules = false
    config.setFrom("$projectDir/config/detekt/detekt.yml")
    baseline = file("$projectDir/config/detekt/baseline.xml")
}

tasks.withType<io.gitlab.arturbosch.detekt.Detekt>().configureEach {
    reports {
        html.required.set(true)
        xml.required.set(true)
        txt.required.set(true)
        sarif.required.set(true)
    }
}

dependencies {
    detektPlugins("io.gitlab.arturbosch.detekt:detekt-formatting:1.23.4")
}


// Jacoco configuration for code coverage
subprojects {
    apply(plugin = "jacoco")
    
    jacoco {
        toolVersion = "0.8.11"
    }
    
    tasks.withType<Test> {
        configure<JacocoTaskExtension> {
            isIncludeNoLocationClasses = true
            excludes = listOf("jdk.internal.*")
        }
    }
}

// Task to generate unified coverage report
tasks.register("jacocoTestReport", JacocoReport::class) {
    group = "Reporting"
    description = "Generate Jacoco coverage reports for all modules"
    
    reports {
        xml.required.set(true)
        html.required.set(true)
        csv.required.set(false)
    }
    
    val excludes = listOf(
        "**/R.class",
        "**/R$*.class",
        "**/BuildConfig.*",
        "**/Manifest*.*",
        "**/*Test*.*",
        "android/**/*.*",
        "**/*\$ViewInjector*.*",
        "**/*\$ViewBinder*.*",
        "**/Lambda$*.class",
        "**/Lambda.class",
        "**/*Lambda.class",
        "**/*Lambda*.class",
        "**/*_MembersInjector.class",
        "**/Dagger*Component*.*",
        "**/*Module_*Factory.class",
        "**/di/module/*",
        "**/*_Factory*.*",
        "**/*Module*.*",
        "**/*Dagger*.*",
        "**/*Hilt*.*",
        "**/hilt_aggregated_deps/*",
        "**/*_HiltModules*.*",
        "**/*_ComponentTreeDeps*.*",
        "**/*_Impl*.*",
        "**/*Binding*.*"
    )
    
    val javaClasses = fileTree(project.rootDir) {
        include(
            "**/build/intermediates/javac/*/classes/**/*.class",
            "**/build/tmp/kotlin-classes/**/*.class"
        )
        exclude(excludes)
    }
    
    val kotlinClasses = fileTree(project.rootDir) {
        include("**/build/tmp/kotlin-classes/**/*.class")
        exclude(excludes)
    }
    
    classDirectories.setFrom(files(javaClasses, kotlinClasses))
    
    val sourceDirs = files(
        fileTree(project.rootDir) {
            include(
                "**/src/main/java/**",
                "**/src/main/kotlin/**"
            )
        }
    )
    
    sourceDirectories.setFrom(sourceDirs)
    
    executionData.setFrom(
        fileTree(project.rootDir) {
            include(
                "**/build/jacoco/*.exec",
                "**/build/outputs/unit_test_code_coverage/**/*.exec"
            )
        }
    )
}

// Task to verify minimum coverage threshold
tasks.register("jacocoTestCoverageVerification", JacocoCoverageVerification::class) {
    group = "Verification"
    description = "Verify minimum code coverage threshold (70%)"
    
    violationRules {
        rule {
            limit {
                minimum = "0.70".toBigDecimal()
            }
        }
    }
    
    val excludes = listOf(
        "**/R.class",
        "**/R$*.class",
        "**/BuildConfig.*",
        "**/Manifest*.*",
        "**/*Test*.*",
        "android/**/*.*",
        "**/*\$ViewInjector*.*",
        "**/*\$ViewBinder*.*",
        "**/Lambda$*.class",
        "**/Lambda.class",
        "**/*Lambda.class",
        "**/*Lambda*.class",
        "**/*_MembersInjector.class",
        "**/Dagger*Component*.*",
        "**/*Module_*Factory.class",
        "**/di/module/*",
        "**/*_Factory*.*",
        "**/*Module*.*",
        "**/*Dagger*.*",
        "**/*Hilt*.*",
        "**/hilt_aggregated_deps/*",
        "**/*_HiltModules*.*",
        "**/*_ComponentTreeDeps*.*",
        "**/*_Impl*.*",
        "**/*Binding*.*"
    )
    
    classDirectories.setFrom(
        fileTree(project.rootDir) {
            include(
                "**/build/intermediates/javac/*/classes/**/*.class",
                "**/build/tmp/kotlin-classes/**/*.class"
            )
            exclude(excludes)
        }
    )
    
    executionData.setFrom(
        fileTree(project.rootDir) {
            include(
                "**/build/jacoco/*.exec",
                "**/build/outputs/unit_test_code_coverage/**/*.exec"
            )
        }
    )
}
