pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "RideConnect"

include(":rider-app")
include(":driver-app")
include(":core:domain")
include(":core:data")
include(":core:network")
include(":core:database")
include(":core:common")
include(":core:ui")
