<template>
  <nav class="navbar navbar-light">
    <div class="container">
      <ul v-if="!isAuthenticated" class="nav navbar-nav pull-xs-right">
        <li class="nav-item">
          <router-link
            class="nav-link"
            active-class="active"
            exact
            :to="{ name: 'Home' }"
          >
            Home
          </router-link>
        </li>
        <li class="nav-item">
          <router-link
            class="nav-link"
            active-class="active"
            exact
            :to="{ name: 'wits' }"
          >
            Wits
          </router-link>
        </li>
      </ul>
    </div>
  </nav>
</template>

<script>
export default {
  name: "SGHeader"
};
</script>
