<template>
  <v-app>
    <v-app-bar app color="primary" dark dense>
      <v-toolbar-title class="text-h5 mr-3"
        ><span class="font-weight-light">FIGURE</span
        ><span class="font-weight-thin">OUT</span></v-toolbar-title
      >

      <v-spacer></v-spacer>

      <v-btn
        href="https://github.com/TechnionTDK/figure-out"
        target="_blank"
        text
      >
        <span class="mr-2">GitHub</span>
        <v-icon>mdi-open-in-new</v-icon>
      </v-btn>
    </v-app-bar>

    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script>
export default {
  name: "App",

  data: () => ({
    //
  }),
};
</script>
